import sys
import re

keywords = { 'if' : 'IF',
             'then' : 'THEN',
             'else' : 'ELSE',
             'begin' : 'BEGIN',
             'end' : 'END',
             'while' : 'WHILE',
             'do' : 'DO',
             'program' : 'PROGRAM',
             'var' : 'VAR',
             'as' : 'AS',
             'int' : 'INT',
             'bool' : 'BOOL'}
builtinFunctions = { 'writeInt' : 'WRITEINT',
                     'readInt' : 'READINT'}
symbols = { '(' : 'LP',
            ')' : 'RP',
            ':=' : 'ASGN',
            ';' : 'SC',
            '*' : 'MULTIPLICATIVE(*)',
            'div' : 'MULTIPLICATIVE(div)',
            'mod' : 'MULTIPLICATIVE(mod)',
            '+' : 'ADDITIVE(+)',
            '-' : 'ADDITIVE(-)',
            '=' : 'COMPARE(=)',
            '!=' : 'COMPARE(!=)',
            '<' : 'COMPARE(<)',
            '>' : 'COMPARE(>)',
            '<=' : 'COMPARE(<=)',
            '>=' : 'COMPARE(>=)' }

class TokenStream():
    def __init__(self):
        self.tokens = []

    def addToken(self, token):
        self.tokens.append(token)

ts = TokenStream()

def lexer(inputFile, baseName):
    validFlag = True
    outputFile = baseName + ".tok"
    lineNumber = 0

    try:
        #open input file
        source = open(inputFile, 'r')
    except OSError:
        print("Invalid File: " + inputFile)
        sys.exit(2)

    try:
        #open/create outputfile
        output = open(outputFile, 'w')
    except OSError:
        print("Unable to create and read output file: " + outputFile)
        sys.exit(2)

    #loop and read line by line
    #print tokens to fileName.tok, one token per line
    for line in source:
        lineNumber += 1

        #check for new comment
        commentArray = line.split('%')
        if len(commentArray) > 1 and not commentArray[0]:
            continue

        #split line into tokens
        tokenArray = commentArray[0].split()

        #loop through array of tokens
        for tok in tokenArray:
            if processToken(tok, lineNumber, output):
                continue
            else:
                validFlag = False

    source.close()
    output.close()
    return validFlag, ts.tokens

def processToken(tok, lineNumber, output):
    if validToken(tok, output, lineNumber):
        return True

    #else check substrings to see if it's two tokens without whitespace
    subStringLength = len(tok) - 1
    if not findSubTok(tok, subStringLength, output, lineNumber):
        print("SCANNER ERROR. Line: " + str(lineNumber)
        + " Cause: '" + tok + "'")
        return False

    return True

def findSubTok(tok, subStringLength, output, ln):
    if subStringLength < 1:
        return False

    if validToken(tok[:subStringLength], output, ln):
        if validToken(tok[subStringLength:], output, ln):
            return True
        else:
            return findSubTok(tok[subStringLength:], (len(tok)-subStringLength)-1, output, ln)
    else:
        return findSubTok(tok, subStringLength-1, output, ln)

def validToken(tok, output, ln):
    #attempt to match keywords
    if tok in keywords:
        output.write(keywords[tok] + "\n")
        ts.addToken((keywords[tok], ln))
        return True, keywords[tok]

    #match built-in functions
    if tok in builtinFunctions:
        output.write(builtinFunctions[tok] + "\n")
        ts.addToken((builtinFunctions[tok], ln))
        return True, builtinFunctions[tok]

    #match syms and ops
    if tok in symbols:
        output.write(symbols[tok] + "\n")
        ts.addToken((symbols[tok], ln))
        return True, symbols[tok]

    #match numbers, literals, idents
    if re.match("^[1-9][0-9]*$", tok) or tok == "0":
        output.write("num(" + tok + ")" + "\n")
        ts.addToken(("num(" + tok + ")", ln))
        return True, "num(" + tok + ")"
    if tok == "false" or tok == "true":
        output.write("boollit("+ tok +")" + "\n")
        ts.addToken(("boollit("+ tok +")", ln))
        return True
    if re.match("^[a-z_A-Z][a-zA-Z0-9]*$", tok):
        output.write("ident("+ tok +")" + "\n")
        ts.addToken(("ident("+ tok +")", ln))
        return True, "ident("+ tok +")"

    return False