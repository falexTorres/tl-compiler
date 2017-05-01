from parser.SyntaxChecker import Checker
from parser.Node import Node
import sys

class Builder:
    def __init__(self):
        self.yo = 'cool'

    @staticmethod
    def addDeclarations(self, decl_list_node):
        while(Checker.isDeclarations(self.tokens) != 0):
            self.advanceToken() # advance past VAR token
            identifier_name = self.getCurrentToken()[0].split('(')[1].split(')')[0]
            self.advanceToken() # advance past identifier token
            self.advanceToken() # advance past AS token
            identifier_type = self.getCurrentToken()[0].lower()
            self.advanceToken() # advance past type token
            self.advanceToken() # advance past SC token
            decl_node = Node(identifier_name, self.getCurrentToken()[1], 2, 0, identifier_type, decl_list_node)
            self.addNode(decl_node)

    # adds asgn node and identifier node and returns asgn node
    @staticmethod
    def addAssignment(self, top_node):
        asgn_node = Node(':=', self.getCurrentToken()[1], top_node.tree_level + 1, 2, parent=top_node) # create ASGN node
        identifier_name = self.getCurrentToken()[0].split('(')[1].split(')')[0]
        ident_node = Node(identifier_name, self.getCurrentToken()[1], asgn_node.tree_level + 1, 3, parent=asgn_node)
        self.addNode(ident_node)
        self.advanceToken() # advance past identifier token
        self.addNode(asgn_node)
        self.advanceToken() # advance past ASGN token
        if self.getCurrentToken()[0] == 'READINT':
            asgn_node.expression_type = 'int'
            ident_node.expression_type = 'int'
            readInt_node = Node('readInt', self.getCurrentToken()[1], asgn_node.tree_level + 1, 3, 0, parent=asgn_node)
            self.advanceToken() # advance past READINT token
            self.addNode(readInt_node)
            return asgn_node
        expression_node = Builder.addExpression(self, asgn_node)
        asgn_node.expression_type = expression_node.expression_type
        ident_node.expression_type = expression_node.expression_type
        return asgn_node

    @staticmethod
    def addIfStatement(self, top_node):
        if_node = Node('if', self.getCurrentToken()[1], top_node.tree_level + 1, 1, parent=top_node)
        self.addNode(if_node)
        self.advanceToken() # advance past IF token
        expression_node = Builder.addExpression(self, if_node)
        self.advanceToken() # advance past THEN token
        stmt_seq_node = Builder.addIfStatementSequence(self, if_node)
        if Checker.isElseClause(self.tokens) != False:
            else_node = Builder.addElseClause(self, top_node)
        self.advanceToken() # advance past END token
        return if_node

    def addElseClause(self, top_node):
        self.advanceToken() # advance past ELSE token
        return Builder.addStatementSequence(self, top_node)

    @staticmethod
    def addWhileStatement(self, top_node):
        while_node = Node('while', self.getCurrentToken()[1], top_node.tree_level + 1, 1, parent=top_node)
        self.addNode(while_node)
        self.advanceToken() # advance past WHILE token
        expression_node = Builder.addExpression(self, while_node)
        self.advanceToken() # advance past DO token
        stmt_seq_node = Builder.addStatementSequence(self, while_node)
        self.advanceToken() # advance past END token
        return while_node

    @staticmethod
    def addWriteInt(self, top_node):
        writeInt_node = Node('writeInt', self.getCurrentToken()[1], top_node.tree_level + 1, 1, 0, parent=top_node)
        self.addNode(writeInt_node)
        self.advanceToken() # advance past WRITEINT token
        expression_node = Builder.addExpression(self, writeInt_node)
        return writeInt_node

    # adds expression to AST and returns top node of expression
    @staticmethod
    def addExpression(self, top_node):
        tokens = Checker.isSimpleExpression(self.tokens)
        if 'COMPARE' in tokens[0][0].split('(')[0]:
            # is compare expression
            inequality = tokens[0][0].split('(')[1].split(')')[0]
            compare_node = Node(inequality, tokens[0][1], top_node.tree_level + 1, 2, 1, parent=top_node)
            self.addNode(compare_node)
            simpleExpression_node = Builder.addSimpleExpression(self, compare_node)
            self.advanceToken() # advance past COMPARE token
            expression_node = Builder.addExpression(self, compare_node)
            return compare_node
        # is simple expression
        return Builder.addSimpleExpression(self, top_node)

    @staticmethod
    def addSimpleExpression(self, top_node):
        tokens = Checker.isTerm(self.tokens)
        if 'ADDITIVE' in tokens[0][0].split('(')[0]:
            # is additive simple expression
            operator = tokens[0][0].split('(')[1].split(')')[0]
            add_node = Node(operator, tokens[0][1], top_node.tree_level + 1, 2, 0, parent=top_node)
            self.addNode(add_node)
            term_node = Builder.addTerm(self, add_node)
            self.advanceToken() # advance past ADDITIVE token
            simpleExpression_node = Builder.addSimpleExpression(self, add_node)
            return add_node
        return Builder.addTerm(self, top_node)

    @staticmethod
    def addTerm(self, top_node):
        tokens = Checker.isFactor(self.tokens)
        if 'MULTIPLICATIVE' in tokens[0][0].split('(')[0]:
            operator = tokens[0][0].split('(')[1].split(')')[0]
            mult_node = Node(operator, tokens[0][1], top_node.tree_level + 1, 2, 0, parent=top_node)
            self.addNode(mult_node)
            factor_node = Builder.addFactor(self, mult_node)
            self.advanceToken() # advance past MULTIPLICATIVE token
            term_node = Builder.addTerm(self, mult_node)
            return mult_node
        return Builder.addFactor(self, top_node)

    @staticmethod
    def addFactor(self, top_node):
        if self.getCurrentToken()[0] == 'LP':
            self.advanceToken() # advance past LP token
            simpleExpression_node = Builder.addSimpleExpression(self, top_node)
            self.advanceToken() # advance past RP token
            return simpleExpression_node
        if self.getCurrentToken()[0].split('(')[0] == 'num':
            num = self.getCurrentToken()[0].split('(')[1].split(')')[0]
            factor_node = Node(num, self.getCurrentToken()[1], top_node.tree_level + 1, 3, 0, parent=top_node)
            self.addNode(factor_node)
            self.advanceToken() # advance past num token
            return factor_node
        if self.getCurrentToken()[0].split('(')[0] == 'boollit':
            boole = self.getCurrentToken()[0].split('(')[1].split(')')[0]
            factor_node = Node(boole, self.getCurrentToken()[1], top_node.tree_level + 1, 3, 1, parent=top_node)
            self.addNode(factor_node)
            self.advanceToken() # advance past boollit token
            return factor_node
        if self.getCurrentToken()[0].split('(')[0] == 'ident':
            identifier = self.getCurrentToken()[0].split('(')[1].split(')')[0]
            factor_node = Node(identifier, self.getCurrentToken()[1], top_node.tree_level + 1, 3, 0, parent=top_node)
            self.addNode(factor_node)
            self.advanceToken() # advance past ident token
            return factor_node

    @staticmethod
    def addStatement(self, top_node):
        if Checker.isAssignment(self.tokens) != False:
            return Builder.addAssignment(self, top_node)
        elif Checker.isIfStatement(self.tokens) != False:
            return Builder.addIfStatement(self, top_node)
        elif Checker.isWhileStatement(self.tokens) != False:
            return Builder.addWhileStatement(self, top_node)
        elif Checker.isWriteInt(self.tokens) != False:
            return Builder.addWriteInt(self, top_node)
        print("\nNOT A STATEMENT\n")
        sys.exit(2)

    @staticmethod
    def addStatementSequence(self, top_node):
        stmt_seq_node = Node('stmt list', self.getCurrentToken()[1], top_node.tree_level + 1, 1, parent=top_node)
        self.addNode(stmt_seq_node)
        while(Checker.isStatement(self.tokens) != False):
            Builder.addStatement(self, stmt_seq_node)
            self.advanceToken() # advance past SC token

        return stmt_seq_node

    @staticmethod
    def addIfStatementSequence(self, top_node):
        stmt_seq_node = Node('stmt list', self.getCurrentToken()[1], top_node.tree_level + 1, 1, parent=top_node)
        self.addNode(stmt_seq_node)
        while(Checker.isStatement(self.tokens) != False):
            Builder.addStatement(self, stmt_seq_node)
            self.advanceToken() # advance past SC token

        return stmt_seq_node

