import sys

from ASTverification import ast_verify, printTree
from codegen.codeGeneration import generate_code
from parser.ParseRv5 import Parser
from scanner import lexer

if len(sys.argv) < 2:
    print("Usage: " + sys.argv[0] + " <input file>")
    sys.exit(2)

#get file name
inputFile = sys.argv[1]
#get the base name of the program being compiled
base_name = inputFile.split('.', 1)
base_name = base_name[0]

#send inputfile to lexer/scanner
lexer_flag, tokens = lexer(inputFile, base_name)

if not lexer_flag:
    print("\ncompilation failed due to LEXICAL error\n")
    sys.exit(2)

parser = Parser(base_name)
parser_flag, ast = parser.parse(tokens)


if not parser_flag:
    print("\ncompilation failed due to PARSING error\n")
    sys.exit(2)

parser_flag, ast, symbolTable = ast_verify(ast)

if parser_flag > 0:
    print("\ncompilation failed due to TYPE error\n")
    sys.exit(2)

generate_code(ast)

print("\nCompilation of " + inputFile + " successful\n")   
