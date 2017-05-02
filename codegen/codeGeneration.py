import re

from codegen.block import Block
import parser.ASTree

operators = ['*', 'div', 'mod', '+', '-', '=', '!=', '<', '>', '<=', '>=']


def generate_code(ast, base_name):
    rootBlock = three_code_gen(ast)

    with open(base_name + '.cfg.dot', 'w') as output:
        output.write(create_controlflow_graphviz(rootBlock))
        output.close()


def three_code_gen(ast):
    # create the root block
    rootBlock = Block()

    three_code_walk_ast(rootBlock, ast)

    # print(create_controlflow_graphviz(rootBlock))

    return rootBlock


def three_code_walk_ast(block, ast, parent='program', symTable = None):
    # base case is null
    if not ast:
        return

    if not symTable:
        symTable = {}
        symTable['pointer'] = 0

    # list of items that will be returned from children
    retArgs = []

    # assignBlock
    # Used for passing down blocks
    assignBlock = block

    # call each child and append it's return item to the list
    # block generation here also
    for child in ast.children:
        # handle if and while child nodes
        # They need a new block
        if child.label == 'if' or child.label == 'while':
            # create the cond block
            assignBlock.thenBlock = Block()
            assignBlock.thenBlock.entryBlock = assignBlock

            # create the else or resume block
            assignBlock.thenBlock.elseBlock = Block()
            assignBlock.thenBlock.elseBlock.entryBlock = assignBlock.thenBlock

            retArgs.append(three_code_walk_ast(assignBlock.thenBlock, child, ast.label, symTable))

            assignBlock = assignBlock.thenBlock.elseBlock

        # 4 cases
        # case 1: stmt list is the parent
        #   The child is an else statement
        #   The current block should be an empty block from the previous if statement
        #   so the current block is given to the stmt list child and a new resume
        #   block is created.
        # case 2: if is parent
        #   Create a new block that will be the then block for the cond block
        # case 3: while is parent
        #   Create a new block that will be the then block
        # case 4: program is parent
        #    do nothing
        elif child.label == 'stmt list':
            if ast.label == 'stmt list':
                retArgs.append(three_code_walk_ast(assignBlock, child, ast.label, symTable))

                # resume block for else statement
                assignBlock.thenBlock = Block()
                assignBlock.thenBlock.entryBlock = assignBlock

                # connect the if statement's then block to the resume
                assignBlock.entryBlock.thenBlock.thenBlock = assignBlock.thenBlock

                assignBlock = assignBlock.thenBlock

            # create the then block for the cond block
            elif ast.label == 'if':
                assignBlock.thenBlock = Block()
                assignBlock.thenBlock.entryBlock = assignBlock

                retArgs.append(three_code_walk_ast(assignBlock.thenBlock, child, ast.label, symTable))

            elif ast.label == 'while':
                # block for inside while loop
                assignBlock.thenBlock = Block()
                assignBlock.thenBlock.entryBlock = assignBlock

                # connect the inside of while loop to cond block
                assignBlock.thenBlock.thenBlock = assignBlock

                retArgs.append(three_code_walk_ast(assignBlock.thenBlock, child, ast.label, symTable))
            else:
                retArgs.append(three_code_walk_ast(assignBlock, child, ast.label, symTable))

        else:
            retArgs.append(three_code_walk_ast(assignBlock, child, ast.label, symTable))

    ######################################################################################
    # Handle the ast node type
    # MIPS instructions are in the form of
    # instr dest, source1, source2

    if ast.label == 'program':
        pass

    # take the declaration instructions and add it to the block
    elif ast.label == 'decl list':
        for decl in retArgs:
            if decl:
                block.add_instruction(decl)
        return ""

    # Take the list of instructions from the child nodes
    # Places instructions into the current block
    # If a child returns a block, then the current block is now
    # that one (for the if statements and while statements)
    #
    # while statement - pack given instructions into current block
    # if statement - pack given instructions into current block
    # (then block)
    # stmt list - This is the else block of the previous if statement
    # store instructions into the current block and create a new block
    # that will be the resume block out of the if
    elif ast.label == 'stmt list':
        for ret in retArgs:
            if isinstance(ret, Block):
                block.add_instruction("j {0}".format(block.thenBlock.label))
                block = ret
            else:
                if ret:
                    block.add_instruction(ret)

        if parent == 'stmt list':
            return block.thenBlock

        if not block.thenBlock:
            block.add_instruction("li $v0, 10")
            block.add_instruction("syscall")
        else:
            block.add_instruction("j {0}".format(block.thenBlock.label))

    # decl:name:type
    # adds instruction, loadl 0 => r_name
    elif ast.label[:5] == 'decl:':
        match = re.findall(r'(?<=[\'\"]).*?(?=[\'\"])', ast.label)
        if match:
            variable = match[0]
        else:
            variable = ast.label.split(':')[1]
        # add variable to symTable and decrease the pointer value
        symTable[variable] = symTable['pointer']
        symTable['pointer'] -= 4

        instructionList = []
        instructionList.append("li $t0, 0")
        instructionList.append("sw $t0, {}($fp)".format(symTable[variable]))
        return instructionList

    # :=
    # assignment operator

    elif ast.label[:2] == ':=':
        instructionList = []
        if isinstance(retArgs[1], list):
            # for instr in retArgs[1]:
            #     if instr:
            #         instructionList.append(instr)
            instructionList.extend(retArgs[1])
            if not ast.children[1].label.split(':')[0] == 'readInt':
                sourceReg = instructionList[-1].split()[2][:-5]
                instructionList.append("lw $t1, {}($fp)".format(sourceReg))
        else:
            if retArgs[1] in symTable:
                sourceReg = symTable[retArgs[1]]
            else:
                symTable[retArgs[1]] = symTable['pointer']
                symTable['pointer'] -= 4
                sourceReg = symTable[retArgs[1]]
                instructionList.append("li $t0, {}".format(retArgs[1]))
                instructionList.append("sw $t0, {}($fp)".format(sourceReg))
            instructionList.append("lw $t1, {}($fp)".format(sourceReg))

        if ast.children[1].label.split(':')[0] == 'readInt':
            instructionList.append("add $t0, $v0, $zero")
        else:
            instructionList.append("add $t0, $t1, $zero".format())

        instructionList.append("sw $t0, {}($fp)".format(symTable[retArgs[0]]))
        return instructionList

    # if
    # add the bool calculation (retArgs[0]) to the current block.
    #
    elif ast.label == 'if':
        # check if the inside of the if statement is connected
        # if not, then there isn't an else statement
        # and the if inside needs to be connected
        if not block.thenBlock.thenBlock:
            block.thenBlock.thenBlock = block.elseBlock

        # add jump from previous block to this cond block
        # block.entryBlock.add_instruction("j {0}".format(block.entryBlock.label))

        # add cond calculation to current block
        block.add_instruction(retArgs[0])

        # grab the cmp stack address
        cmpReg = block.instructions[-1].split()[2][:-5]
        block.add_instruction("lw $t0, {}($fp)".format(cmpReg))
        # branch option
        # branches to then block
        block.add_instruction("bne $t0, $zero, {}".format(block.thenBlock.label))

        # add the jump for the else block
        block.add_instruction("j {}".format(block.elseBlock))

        # return the resume block. cond blk -> inside blk -> resume
        return block.thenBlock.thenBlock

    elif ast.label == 'while':
        # add jump from previous block to this cond block
        # block.entryBlock.add_instruction("j {0}".format(block.entryBlock.label))

        # add cond calculation to current block
        block.add_instruction(retArgs[0])

        # grab the cmp stack address
        cmpReg = block.instructions[-1].split()[2][:-5]
        block.add_instruction("lw $t0, {}($fp)".format(cmpReg))
        # branch option
        # branches to then block
        block.add_instruction("bne $t0, $zero, {}".format(block.thenBlock.label))

        # add the jump for the else block
        block.add_instruction("j {}".format(block.elseBlock))

        # return the resume block
        return block.elseBlock

    elif ast.label[:7] == 'readInt':
        instructionList = []
        # instructionList.append("# readInt")
        instructionList.append("li $v0, 5")
        instructionList.append("syscall")

        return instructionList

    elif ast.label[:8] == 'writeInt':
        instructionList = []

        # get the other instructions of calculations
        if isinstance(retArgs[0], list):
            # for instr in retArgs[0]:
            #     if instr:
            #         instructionList.append(instr)
            instructionList.extend(retArgs[0])

            # grab the last instruction which should be
            # sw $t0, symTable[]($fp)
            # Splits the instruction by whitespace and grabs the last operand
            # then grabs the number before ($fp)
            source = instructionList[-1].split()[2][:-5]
        else:
            if retArgs[0] in symTable:
                source = symTable[retArgs[0]]
            else:
                symTable[retArgs[0]] = symTable['pointer']
                symTable['pointer'] -= 4
                source = symTable[retArgs[0]]
                instructionList.append("li $t0, {}".format(retArgs[0]))
                instructionList.append("sw $t0, {}($fp)".format(source))

        instructionList.append("li $v0, 1")
        instructionList.append("lw $t1, {}($fp)".format(source))
        instructionList.append("add $a0, $t1, $zero")
        instructionList.append("syscall")
        instructionList.append("li $v0, 4")
        instructionList.append("la $a0, newline")
        instructionList.append("syscall")

        return instructionList

    # operations that take two operands
    # multiply, div, mod, add, subtract, compare
    elif ast.label.split(':')[0] in operators:

        instructionList = []

        # left side
        if isinstance(retArgs[0], list):
            # for instr in retArgs[0]:
            #     if instr:
            #         instructionList.append(instr)
            instructionList.extend(retArgs[0])

            # grab the last instruction which should be
            # sw $t0, symTable[]($fp)
            # Splits the instruction by whitespace and grabs the last operand
            # then grabs the number before ($fp)
            sourceLeft = instructionList[-1].split()[2][:-5]
        else:
            if retArgs[0] in symTable:
                sourceLeft = symTable[retArgs[0]]
            else:
                symTable[retArgs[0]] = symTable['pointer']
                symTable['pointer'] -= 4
                sourceLeft = symTable[retArgs[0]]
                instructionList.append("li $t0, {}".format(retArgs[0]))
                instructionList.append("sw $t0, {}($fp)".format(sourceLeft))

        # right side
        if isinstance(retArgs[1], list):
            # for instr in retArgs[1]:
            #     if instr:
            #         instructionList.append(instr)
            instructionList.extend(retArgs[1])

            # grab the last instruction which should be
            # sw $t0, symTable[]($fp)
            # Splits the instruction by whitespace and grabs the last operand
            # then grabs the number before ($fp)
            sourceRight = instructionList[-1].split()[2][:-5]
        else:
            if retArgs[1] in symTable:
                sourceRight = symTable[retArgs[1]]
            else:
                symTable[retArgs[1]] = symTable['pointer']
                symTable['pointer'] -= 4
                sourceRight = symTable[retArgs[1]]
                instructionList.append("li $t0, {}".format(retArgs[1]))
                instructionList.append("sw $t0, {}($fp)".format(sourceRight))

        # instructionList.append("# {}".format(ast.label.split(':')[0]))

        # load the left operand
        instructionList.append("lw $t1, {}($fp)".format(sourceLeft))

        # load the right operand
        instructionList.append("lw $t2, {}($fp)".format(sourceRight))


        if ast.label[:1] == '*':
            instructionList.append("mult $t0, $t1, $t2")
        elif ast.label[:3] == 'div':
            instructionList.append("div $t0, $t1, $t2")
        elif ast.label[:3] == 'mod':
            instructionList.append("rem $t0, $t1, $t2")
        elif ast.label[:1] == '+':
            instructionList.append("add $t0, $t1, $t2")
        elif ast.label[:1] == '-':
            instructionList.append("sub $t0, $t1, $t2")
        elif ast.label[:1] == '=':
            instructionList.append("seq $t0, $t1, $t2")
        elif ast.label[:1] == '!':
            instructionList.append("sne $t0, $t1, $t2")
        elif ast.label[:2] == '<=':
            instructionList.append("sle $t0, $t1, $t2")
        elif ast.label[:2] == '>=':
            instructionList.append("seq $t0, $t1, $t2")
        elif ast.label[:1] == '<':
            instructionList.append("slt $t0, $t1, $t2")
        elif ast.label[:1] == '>':
            instructionList.append("sgt $t0, $t1, $t2")


        storeAddress = symTable['pointer']
        symTable['pointer'] -= 4
        instructionList.append("sw $t0, {}($fp)".format(storeAddress))

        return instructionList

    # variables
    else:
        var = ast.label.split(':')[0]
        # if not re.match("^[0-9]+$", var):
        #     return "r_{0}".format(var)
        # else:
        #     return var
        return var


def create_controlflow_graphviz(rootBlock):
    controlFlowString = "digraph tl16ControlFlow {\n   node [shape = box];\n" \
                        "   edge [tailport = s];\n   color=\"/x11/white\"\n"

    controlFlowString += "   entry\n"
    controlFlowString += block_to_string_walk(rootBlock)
    controlFlowString += "}"

    return controlFlowString


def block_to_string_walk(block):
    if not block.instructions:
        return ""

    controlFlowString = "   {0} [label=<<TABLE ALIGN=\"LEFT\" border=\"0\"> " \
                        "   <TR><TD border=\"1\" colspan=\"3\">{1}</TD></TR>\n".format(block.label, block.label)

    # add instructions to the node
    for instr in block.instructions:
        controlFlowString += "   <TR><TD>{0}</TD></TR>\n".format(instr)
    controlFlowString += "   </TABLE> >, ];\n\n"

    # add edges
    if not block.entryBlock:
        controlFlowString += "   entry -> {0}\n".format(block.label)
    if block.thenBlock:
        if not block.thenBlock.instructions:
            controlFlowString += "   exit\n   {0} -> exit\n".format(block.label)
        else:
            controlFlowString += "   {0} -> {1}\n".format(block.label, block.thenBlock.label)
        # stop while loop from causing a loop
        if block.entryBlock and block.thenBlock.label == block.entryBlock.label:
            pass
        else:
            controlFlowString += block_to_string_walk(block.thenBlock)

    if block.elseBlock:
        if not block.elseBlock.instructions:
            controlFlowString += "   exit\n   {0} -> exit\n".format(block.label)
        else:
            controlFlowString += "   {0} -> {1}\n".format(block.label, block.elseBlock.label)

        controlFlowString += block_to_string_walk(block.elseBlock)

    if not block.thenBlock and not block.elseBlock:
        controlFlowString += "   exit\n   {0} -> exit\n".format(block.label)

    return controlFlowString


#DEBUG
if __name__ == "__main__":
    import sys
    three_code_gen(None)
