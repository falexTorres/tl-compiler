class Checker:
	def __init__(self):
		self.sweet = 'dude'

	# returns 0 if empty string, -1 if error, and 1 if correct
	@staticmethod
	def isDeclarations(tokens):
		if tokens[0][0] == 'BEGIN':
			return 0
		if tokens[0][0] != 'VAR':
			return -1
		tokens = tokens[1:] # advance past VAR token
		if tokens[0][0].split('(')[0] != 'ident':
			return -1
		tokens = tokens[1:]
		if tokens[0][0] != 'AS':
			return -1
		tokens = tokens[1:] # advance past AS token
		if tokens[0][0] != 'INT' and tokens[0][0] != 'BOOL':
			return -1
		tokens = tokens[1:] # advance past type token
		if tokens[0][0] != 'SC':
			return -1
		tokens = tokens[1:] # advance past SC token
		if tokens[0][0] == 'BEGIN':
			return 1
		return Checker.isDeclarations(tokens)

	@staticmethod
	def isStatement(tokens):
		return (Checker.isAssignment(tokens) or Checker.isIfStatement(tokens) or Checker.isWhileStatement(tokens) or Checker.isWriteInt(tokens))

	# returns 0 if empty string, -1 if error, and 1 if correct
	@staticmethod
	def isStatementSequence(tokens):
		if tokens[0][0] == 'END':
			return 0
		tokens = Checker.isStatement(tokens) # get new token set
		if tokens == False:
			return -1
		if tokens[0][0] != 'SC':
			return -1
		tokens = tokens[1:] # advance past SC token
		if tokens[0][0] == 'END':
			return tokens
		return Checker.isStatementSequence(tokens)

	# returns 0 if empty string, -1 if error, and 1 if correct
	@staticmethod
	def isIfStatementSequence(tokens):
		if tokens[0][0] == 'ELSE' or tokens[0][0] == 'END':
			return tokens
		tokens = Checker.isStatement(tokens) # get new token set
		if tokens == False:
			return False
		if tokens[0][0] != 'SC':
			return False
		tokens = tokens[1:] # advance past SC token
		return Checker.isIfStatementSequence(tokens)

	@staticmethod
	def isAssignment(tokens):
		if tokens[0][0].split('(')[0] != 'ident':
			return False
		tokens = tokens[1:] # advance past identifier token
		if tokens[0][0] != 'ASGN':
			return False
		tokens = tokens[1:] # advance past ASGN token
		if tokens[0][0] == 'READINT':
			tokens = tokens[1:] # advance past READINT token
			return tokens
		return Checker.isExpression(tokens)

	@staticmethod
	def isIfStatement(tokens):
		if tokens[0][0] != 'IF':
			return False
		tokens = tokens[1:] # advance past IF token
		tokens = Checker.isExpression(tokens)
		if tokens == False or tokens[0][0] != 'THEN':
			return False
		tokens = tokens[1:] # advance past THEN token
		tokens = Checker.isIfStatementSequence(tokens)
		if tokens == False:
			return False
		tmp = tokens
		tokens = Checker.isElseClause(tokens)
		if tokens == False:
			tokens = tmp
		if tokens[0][0] != 'END':
			return False
		tokens = tokens[1:] # advance past END token
		return tokens

	@staticmethod
	def isElseClause(tokens):
		if tokens[0][0] == 'ELSE':
			tokens = tokens[1:] # advance past ELSE token
			tokens = Checker.isStatementSequence(tokens)
			if tokens == 0 or tokens == -1:
				return False
			return tokens
		return False

	@staticmethod
	def isWhileStatement(tokens):
		if tokens[0][0] != 'WHILE':
			return False
		tokens = tokens[1:] # advance past WHILE token
		tokens = Checker.isExpression(tokens)
		if tokens == False:
			return False
		if tokens[0][0] != 'DO':
			return False
		tokens = tokens[1:] # advance past DO token
		tmp = tokens
		tokens = Checker.isStatementSequence(tokens)
		if tokens == 0:
			tokens = tmp
		if tokens == -1:
			return False
		if tokens[0][0] != 'END':
			return False
		tokens = tokens[1:] # advance past END token
		return tokens

	@staticmethod
	def isWriteInt(tokens):
		if tokens[0][0] != 'WRITEINT':
			return False
		tokens = tokens[1:]
		return Checker.isExpression(tokens)

	@staticmethod
	def isExpression(tokens):
		tokens = Checker.isSimpleExpression(tokens)
		if tokens == False:
			return False
		if 'COMPARE' not in tokens[0][0]:
			return tokens
		tokens = tokens[1:] # advance past COMPARE token
		return Checker.isExpression(tokens)

	@staticmethod
	def isSimpleExpression(tokens):
		tokens = Checker.isTerm(tokens)
		if tokens == False:
			return False
		if 'ADDITIVE' not in tokens[0][0]:
			return tokens
		tokens = tokens[1:] # advance past ADDITIVE token
		return Checker.isSimpleExpression(tokens)

	@staticmethod
	def isTerm(tokens):
		tokens = Checker.isFactor(tokens)
		if tokens == False:
			return False
		if 'MULTIPLICATIVE' not in tokens[0][0]:
			return tokens
		tokens = tokens[1:] # advance past MULTPLICATIVE token
		return Checker.isTerm(tokens)

	@staticmethod
	def isFactor(tokens):
		if tokens[0][0] == 'LP':
			tokens = tokens[1:] # advance past LP token
			tokens = Checker.isSimpleExpression(tokens)
			if tokens == False:
				return False
			if tokens[0][0] != 'RP':
				return False
			tokens = tokens[1:] # advance past RP token
			return tokens
		if tokens[0][0].split('(')[0] == 'ident' or 'num' or 'boollit':
			tokens = tokens[1:] # advance past FACTOR token
			return tokens
		return False

from parser.AstBuilder import Builder