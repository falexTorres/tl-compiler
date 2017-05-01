import re
import sys

import parser.ASTree

# root = None

operators = [':=', '*', 'div', 'mod', '+', '-', '=', '!=', '<', '>', '<=', '>=', 'program',
             'decl', 'stmt', 'readInt', 'writeInt', 'while', 'if']

neutralOp = []


# Main function
# returns error flag, AST, symbol table
def ast_verify(astFile):
    root = ast_gen(astFile)
    return ast_check(root)


def ast_check(root):
    symbolTable = {}
    #printTree(root)
    errorFlag = typeCheck(root, symbolTable)
    #printTree(root)
    #print(astToString(root))

    #return error flag, ast, symbol table
    if errorFlag >= 1:
        return errorFlag, root, None
    else:
        return errorFlag, root, symbolTable


def typeCheck(node, symbolTable):
    # flag to return to indicate if there was an error with the AST
    errorFlag = 0

    # check for decl
    if node.category == 'operator' and node.operator == 'decl':
        if node.value in symbolTable:
            node.isError = True
            errorFlag = 1
            print("TypeError:", node.value, "has already been declared! Line:", node.lineNum)
        else:
            symbolTable[node.value] = node.valueType
    elif node.category == 'variable':
        # check if the variable is in the table
        # print(node)
        if not node.value in symbolTable and not re.match("^[0-9]+$", node.value)\
                and not node.value == 'false' and not node.value == 'true':
            node.isError = True
            errorFlag = 1
            print("TypeError:", node.value, "has not been declared! Line:", node.lineNum)

        if not node.valueType:
            node.valueType = symbolTable[node.value]

    # operator that isn't decl. Type check the children
    elif not (node.operator == 'program' or node.operator == 'decl list'
              or node.operator == 'stmt list'):
        # check for while
        # check while or if
        if node.operator == 'while' or node.operator == 'if':
            # if not len(node.children) == 2:
            #     node.isError = True
            #     errorFlag = 1
            #     print("While has a syntax error. Line:", node.lineNum)
            # else:
            if not node.children[0].valueType == 'bool':
                node.isError = True
                errorFlag = 1
                print("TypeError: While loop expected bool. Line:", node.lineNum)

        # assignment operator
        elif node.operator == ':=':
            if not len(node.children) == 2:
                node.isError = True
                errorFlag = 1
                print("assignment has a syntax error. Line:", node.lineNum)
            else:
                # Catch the case of the parser creating the ast with the operands switched
                if node.children[0].operator == 'readInt' and node.children[1].value in symbolTable:
                    tmpChild = node.children[0]
                    node.children[0] = node.children[1]
                    node.children[1] = tmpChild

                if not node.children[0].value in symbolTable:
                    node.isError = True
                    errorFlag = 1
                    print("TypeError:", node.children[0].value,
                          "cannot be assigned a value. Line:", node.lineNum)
                else:
                    #print(node.children)
                    # Check if assignment is to the readInt function
                    if node.children[1].operator == 'readInt':
                        if not symbolTable[node.children[0].value] == 'int':
                            node.isError = True
                            errorFlag = 1
                            print("TypeError: Type mismatch of assigning readInt",
                                  "(int)",
                                  "to", node.children[0].value, "(",
                                  symbolTable[node.children[0].value],
                                  ") Line:", node.lineNum)
                    # assigning a value to a variable... X = Y or X = 5 or X = 5 + 4
                    else:
                        # print("node:", node)
                        # print(node.children)
                        # print(node.children[1].operator, "\n")
                        assignValueType = None
                        if re.match("^[0-9]+$", str(node.children[1].value)) or node.children[1].operator in operators:
                            assignValueType = 'int'
                        elif node.children[1].value in symbolTable:
                            assignValueType = symbolTable[node.children[1].value]

                        if not symbolTable[node.children[0].value] == assignValueType:
                            node.isError = True
                            errorFlag = 1
                            if node.children[1].value:
                                problem = node.children[1].value
                            else:
                                problem = node.children[1].operator
                            print("TypeError: Type mismatch of assigning", problem,
                                  "(", node.children[1].valueType,")",
                                  "to", node.children[0].value, "(", symbolTable[node.children[0].value],
                                  ") Line:", node.lineNum)

        # operators that can be bool or int need to check that the children are the same type
        # elif node.operator in neutralOp:
            # expectedType = None
            # for child in node.children:
            #     if not expectedType:
            #         expectedType = child.valueType
            #     else:
            #         if not child.valueType == expectedType:
            #             child.isError = True
            #             node.isError = True
            #             if child.value:
            #                 problem = child.value
            #             else:
            #                 problem = child.operator
            #             print("TypeError:", problem, "does not match type", expectedType)

        # If not a neutral op, then it is an op involving ints
        else:
            for child in node.children:
                if child.category == 'variable':
                    if not re.match("^[0-9]+$", child.value):
                        if child.value == 'true' or child.value == 'false' \
                                or not symbolTable[child.value] == 'int':
                            node.isError = True
                            errorFlag = 1
                            print("TypeError:", node.operator, "expected int. Line:", node.lineNum)
                elif not child.valueType == 'int':
                    # child.isError = True
                    node.isError = True
                    errorFlag = 1
                    print("TypeError:", node.operator, "expected int. Line:", node.lineNum)

    for child in node.children:
        retFlag = typeCheck(child, symbolTable)
        if retFlag > 0:
            errorFlag = retFlag
        # errorFlag = typeCheck(child, symbolTable)

    return errorFlag


def printTree(node, level=0):
    print(level*"   ", node.label, "| line:", node.lineNum, "|Op:", node.operator,
          "|Val:", node.value, "|ValType:", node.valueType,
          "|TError:", node.isError, node.children)
    for child in node.children:
        printTree(child, level+1)


def ast_gen(astFile):
    root = None

    source = astFile.split("\n")
    # try:
    #     source = open(astFile, 'r')
    # except OSError:
    #     print("Invalid File: " + astFile)
    #     sys.exit(2)

    nodes = {}
    edgeList = []
    addedRoot = False
    for line in source:

        tokenArray = line.split()
        if not tokenArray:
            continue

        if re.match("^(?!n[0-9]+)", tokenArray[0]):
            continue

        if tokenArray[1] != '->':
            match = re.findall(r'(?<=label=\").*?(?=\")', line)
            label = match[0]

            operator = None
            value = None
            valueType = None
            labelTokens = label.split()
            if label in operators or labelTokens[0] in operators:
                category = "operator"
                operator = label
            else:
                labelSplitByColon = label.split(":")
                #special case for :=:<value type>
                if label[:2] == ":=":
                    category = "operator"
                    operator = ':='

                elif labelSplitByColon[0] in operators:
                    category = "operator"
                    if labelSplitByColon[0] == 'decl':
                        operator = 'decl'
                        match = re.findall(r'(?<=[\'\"]).*?(?=[\'\"])', labelSplitByColon[1])
                        #print(labelSplitByColon)
                        if match:
                            value = match[0]
                        else:
                            value = labelSplitByColon[1]

                        if labelSplitByColon[2] == 'int':
                            valueType = "int"
                        else:
                            valueType = "bool"
                    else:
                        operator = labelSplitByColon[0]
                        if len(labelSplitByColon)>1:
                            valueType = labelSplitByColon[1]
                else:
                    category = "variable"
                    value = labelSplitByColon[0]
                    if len(labelSplitByColon)>1:
                        valueType = labelSplitByColon[1]

            match = re.findall(r'(?<=[/\\][/\\\s*]).*?(?=$)', line)
            lineNum = 0
            if match:
                lineNum = match[0]

            # create the node and add it to the dictionary
            newNode = parser.ASTree.ASTree(label, category, operator, value, valueType, False, None,
                                    lineNum)
            nodes[tokenArray[0]] = newNode
            if not addedRoot:
                root = nodes[tokenArray[0]]
                addedRoot = True

        else:
            if not tokenArray[0] in nodes:
                edgeList.append((tokenArray[0], tokenArray[2]))
            else:
                nodes[tokenArray[0]].add_child(nodes[tokenArray[2]])
    for edge in reversed(edgeList):
        nodes[edge[0]].add_child(nodes[edge[1]])

    return root

def astToString(root):
    global nodeNum
    nodeNum = 0

    astString = "digraph tl16Ast {\n   ordering=out;\n" \
                "   node [shape = box, style = filled, fillcolor=\"white\"];\n"
    nodeList = {}
    astString += astToStringWalkNodes(root, nodeList)
    #print(nodeList)
    astString += astToStringWalkEdges(root, nodeList)
    astString += "}"

    return astString


def astToStringWalkNodes(node, nodeList):
    global nodeNum

    nodeNum += 1
    if node.isError:
        astString = \
            "   n{0} [label=\"{1}\",fillcolor=\"/pastel13/1\"shape=box]\n".format(nodeNum, node.label)
    else:
        astString =\
            "   n{0} [label=\"{1}\",shape=box]\n".format(nodeNum, node.label)

    nodeList[node] = "n{0}".format(nodeNum)
    for child in node.children:
        astString += astToStringWalkNodes(child, nodeList)

    return astString

def astToStringWalkEdges(node, nodeList):
    astString = ""

    for child in node.children:
        astString += "   {0} -> {1}\n".format(nodeList[node], nodeList[child])
        astString += astToStringWalkEdges(child, nodeList)

    return astString


# TMP DEBUG
#ast_verify(sys.argv[1])
