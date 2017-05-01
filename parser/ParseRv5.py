from parser.Node import Node
from parser.ParseTree import ASTree
from parser.SyntaxChecker import Checker
from parser.AstBuilder import Builder
from copy import deepcopy
import sys

class Parser:
	def __init__(self, base_name):
		self.ast = ASTree()
		self.tokens = []
		self.base_name = base_name

	def addNode(self, node):
		self.ast.addNode(node)

	def advanceToken(self):
		self.tokens = self.tokens[1:]

	def getCurrentToken(self):
		return self.tokens[0] # (token, line_number)

	def parse(self, token_stream):
		self.tokens = token_stream

		# DO PROGRAM #
		if self.getCurrentToken()[0] != 'PROGRAM':
			return self.printError()
		program_node = Node(name='program', line=self.getCurrentToken()[0][1], tree_level=0, node_type=2)
		self.addNode(program_node)
		self.advanceToken() # advance past PROGRAM token

		# DO DECLARATIONS #
		flag = Checker.isDeclarations(self.tokens)
		if flag == -1:
			return self.printError('Declarations')
		if flag == 1:
			declaration_node = Node('decl list', self.getCurrentToken()[0][1], 1, 1, parent=program_node)
			self.addNode(declaration_node)
			Builder.addDeclarations(self, declaration_node)

		# DO BEGIN #
		if self.getCurrentToken()[0] != 'BEGIN':
			return self.printError()
		self.advanceToken() # advance past BEGIN token

		# DO STATEMENT SEQUENCE #
		if Checker.isStatementSequence(self.tokens):
			Builder.addStatementSequence(self, program_node)

		if self.getCurrentToken()[0] != 'END':
			return self.printError()
		self.advanceToken() # tokens should be empty after this

		graph_viz = self.ast.getGraphViz(self.base_name)
		if graph_viz == False:
			return self.printError('type')
		return True, graph_viz

	# def addDeclarations(self, decl_list_node):
	# 	while(self.isDeclarations(self.tokens) != 0):
	# 		self.advanceToken() # advance past VAR token
	# 		identifier_name = self.getCurrentToken()[0].split('(')[1].split(')')[0]
	# 		self.advanceToken() # advance past identifier token
	# 		self.advanceToken() # advance past AS token
	# 		identifier_type = self.getCurrentToken()[0].lower()
	# 		self.advanceToken() # advance past type token
	# 		self.advanceToken() # advance past SC token
	# 		decl_node = Node(name=identifier_name, line=self.getCurrentToken()[1], tree_level=2, node_type=0, expression_type=identifier_type, parent=decl_list_node)
	# 		self.addNode(decl_node)

	# def addStatementSequence(self, stmt_seq_node):
	# 	while(self.isStatement(self.tokens)):
	# 		self.addStatement(stmt_seq_node)
	# 		self.advanceToken() # advance past SC token

	# def addStatement(self, top_node):
	# 	if self.isAssignment(self.tokens):
	# 		self.addAssignment(top_node)
	# 	elif self.isIfStatement(self.tokens):
	# 		self.addIfStatement(top_node)
	# 	elif self.isWhileStatement(self.tokens):
	# 		self.addWhileStatement(top_node)
	# 	elif self.isWriteInt(self.tokens):
	# 		self.addWriteInt(top_node)

	# # returns 0 if empty string, -1 if error, and 1 if correct
	# def isDeclarations(self, tokens):
	# 	if tokens[0][0] == 'BEGIN':
	# 		return 0
	# 	if tokens[0][0] != 'VAR':
	# 		return -1
	# 	tokens = tokens[1:] # advance past VAR token
	# 	if tokens[0][0].split('(')[0] != 'ident':
	# 		return -1
	# 	tokens = tokens[1:] # advance past identifier token
	# 	if tokens[0][0] != 'AS':
	# 		return -1
	# 	tokens = tokens[1:] # advance past AS token
	# 	if tokens[0][0] != 'INT' and 'BOOL':
	# 		return -1
	# 	tokens = tokens[1:] # advance past type token
	# 	if tokens[0][0] != 'SC':
	# 		return -1
	# 	tokens = tokens[1:] # advance past SC token
	# 	if tokens[0][0] == 'BEGIN':
	# 		return 1
	# 	return self.isDeclarations(tokens)

	# # returns 0 if empty string, -1 if error, and 1 if correct
	# def isStatementSequence(self, tokens):
	# 	if tokens[0][0] == 'END':
	# 		return 0
	# 	tokens = self.isStatement(tokens) # get new token set
	# 	if not tokens:
	# 		return -1
	# 	if tokens[0][0] != 'SC':
	# 		return -1
	# 	tokens = tokens[1:] # advance past SC token
	# 	if tokens[0][0] == 'END':
	# 		return 1
	# 	return self.isStatementSequence(tokens)

	# # returns 0 if empty string, -1 if error, and 1 if correct
	# def isIfStatementSequence(self, tokens):
	# 	if tokens[0][0] == 'ELSE' or 'END':
	# 		return tokens
	# 	tokens = self.isStatement(tokens) # get new token set
	# 	if not tokens:
	# 		return False
	# 	if tokens[0][0] != 'SC':
	# 		return False
	# 	tokens = tokens[1:] # advance past SC token
	# 	return self.isIfStatementSequence(tokens)

	# def isStatement(self, tokens):
	# 	return self.isAssignment(tokens) or self.isIfStatement(tokens) or self.isWhileStatement(tokens) or self.isWriteInt(tokens)

	# def isAssignment(self, tokens):
	# 	if tokens[0][0].split('(')[0] != 'ident':
	# 		return False
	# 	tokens = tokens[1:] # advance past identifier token
	# 	if tokens[0][0] != 'ASGN':
	# 		return False
	# 	tokens = tokens[1:] # advance past ASGN token
	# 	if tokens[0][0] == 'READINT':
	# 		return tokens
	# 	return self.isExpression(tokens)

	# def isIfStatement(self, tokens):
	# 	if tokens[0][0] != 'IF':
	# 		return False
	# 	tokens = tokens[1:]
	# 	tokens = self.isExpression(tokens)
	# 	if not tokens:
	# 		return False
	# 	if tokens[0][0] != 'THEN':
	# 		return False
	# 	tokens = self.isIfStatementSequence(tokens)
	# 	if not tokens:
	# 		return False
	# 	tokens = self.isElseClause(tokens)
	# 	if tokens[0][0] != 'END':
	# 		return False
	# 	return tokens

	# def isElseClause(self, tokens):
	# 	if tokens[0][0] == 'ELSE':
	# 		return self.isStatementSequence(tokens)
	# 	return tokens


	def printError(self, error='Syntax'):
		try:
			print(self.tokens)
			print("PARSING ERROR:\n\t" + error + ' error on line ' + str(self.getCurrentToken()[1]) + "\n")
		except:
			print("PARSING ERROR:\n\t" + error)
		return False, self.ast

	def printErrorAndExit(self, error='Syntax'):
		print(self.tokens)
		print("PARSING ERROR:\n\t" + error + ' error on line ' + str(self.getCurrentToken()[1]) + "\n")
		sys.exit(2)


