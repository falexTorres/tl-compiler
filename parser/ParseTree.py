class ASTree:
    def __init__(self):
        self.levels = []
        self.nodes = []

    def addNode(self, node):
        if self.getNumberOfLevels() > (node.tree_level - 1):
            nodes = []
            self.levels.append(nodes)
        self.nodes.append(node)
        self.levels[node.tree_level].append(node)

    def getNumberOfLevels(self):
        return len(self.levels)

    def getGraphViz(self, base_name):
        ret_me = 'digraph ' + base_name + '{\n'
        declared_variables = []
        for node in self.nodes:
            if node.node_type == 'declaration':
                variable = Variable(node.name, node.expression_type)
                declared_variables.append(variable)
            ret_me += 'n' + str(node.node_id) + ' [label="' + node.getLabel() + '", shape=box]\n'

        for node in self.nodes:
            if node.node_id == 0:
                continue

            for variable in declared_variables:
                if node.name == variable.name and node.expression_type != variable.type:
                    return False

            ret_me += 'n' + str(node.parent) + ' -> ' + 'n' + str(node.node_id) + '\n'
        ret_me += '}\n'

        with open(base_name + '.ast.dot', 'w') as output:
            output.write(ret_me)

        return ret_me

    def __repr__(self):
        if len(self.nodes) == 0:
            return '\nAST is empty!\n'
        ret_me = ''
        for node in self.nodes:
            ret_me += node.getLabel() + ", "
        return ret_me

class Variable:
    def __init__(self, n, t):
        self.name = n
        self.type = t


