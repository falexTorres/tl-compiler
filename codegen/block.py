import itertools


class Block(object):
    newBlockNum = itertools.count()

    def __init__(self, entryBlock = None, thenBlock = None, elseBlock = None,
                 label = None, instructions = None):
        self.entryBlock = entryBlock
        self.thenBlock = thenBlock
        self.elseBlock = elseBlock
        self.blockNumber = next(Block.newBlockNum)
        self.instructions = []
        if label is not None:
            self.label = label
        else:
            self.label = "Block" + str(self.blockNumber)
        if instructions is not None:
            for instruction in instructions:
                if instruction:
                    self.add_instruction(instruction)

    def __repr__(self):
        return self.label

    def add_instruction(self, instruction):
        # assert isinstance(instruction, Block)
        if isinstance(instruction, list):
            for instr in instruction:
                self.instructions.append(instr)
        else:
            self.instructions.append(instruction)