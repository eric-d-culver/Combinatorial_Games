#!/usr/bin/python3

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from grammar import parser, EvalStatement
from lark import Discard

test = False

def main_loop():
    exit = False
    while not exit:
        statement = prompt("CGS> ", history = FileHistory("history.txt"))
        tree = parser.parse(statement)
        try:
            # PRINT
            print(EvalStatement().transform(tree))
        except Discard as e:
            exit = True
        except Exception as e:
            print(e)

if test:
    tree = parser.parse("{0, ^2*,  *17, g|  1/2^2, 1, v, *}")
    print(tree.pretty())
    try:
        print(EvalStatement().transform(tree))
    except Exception as e:
        print(e)
else:
    main_loop()
