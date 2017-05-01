import sys

node_types = ['declaration', 'at_least_one_child', 'two_children_only', 'terminal']
expression_types = ['int', 'bool']

class Node:
    node_id = 0
    def __init__(self, name, line, tree_level, node_type, expression_type=None, parent=None):
        self.node_type = node_types[node_type]
        self.name = name
        self.line = line
        self.tree_level = tree_level
        self.node_id = Node.node_id
        Node.node_id += 1
        if parent != None:
            self.parent = parent.node_id
        expression_type_bool = expression_type != 0 and expression_type != 1 and expression_type != None and expression_type != 'int' and expression_type != 'bool'
        if expression_type_bool:
            print("expression type " + expression_type + " not a valid type.")
            sys.exit(2)
        if expression_type == 0 or expression_type == 1:
            expression_type = expression_types[expression_type]
        self.expression_type = expression_type

    def getLabel(self):
        if self.name == 'program':
            return self.name
        if self.node_type == 'at_least_one_child':
            return self.name
        elif self.node_type == 'declaration':
            return 'decl:' + self.name + ':' + self.expression_type
        return self.name + ':' + self.expression_type


    def __repr__(self):
        return self.getLabel()
