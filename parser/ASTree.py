class ASTree(object):

    def __init__(self, label='root', category='var', operator=None,
                 value='-1', valueType='int', isError=False,
                 children=None, lineNum=-1):
        self.label = label
        self.category = category
        self.operator = operator
        self.value = value
        self.valueType = valueType
        self.isError = isError
        self.lineNum = lineNum
        self.children = []
        if children is not None:
            for child in children:
                self.add_child(child)

    def __repr__(self):
        return self.label

    def add_child(self, node):
        assert isinstance(node, ASTree)
        self.children.append(node)
