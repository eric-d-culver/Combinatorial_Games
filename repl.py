#!/usr/bin/python3

from lark import Lark, Transformer, GrammarError, Discard
#from lark.exceptions import GrammarException
from games import Game, cmpGames

test = False

heap = {} # stores variables with assignments. Key is variable name, value is Game variable is assigned to

# READ

grammar = r"""
?statement: quit_statement 
         | comparison
         | assignment
         | expression

quit_statement: "quit"

comparison: expression "==" expression -> equal_to
          | expression "<" expression -> less_than
          | expression ">" expression -> greater_than
          | expression "<>" expression -> fuzzy_with
          | expression "<=" expression -> less_equal
          | expression ">=" expression -> greater_equal
          | expression "<|" expression -> less_fuzzy
          | expression "|>" expression -> greater_fuzzy

assignment: name ":=" expression

name: CNAME

?expression: atom
           | sum
           | "-" expression -> negation

sum: sum "+" atom
   | atom

?atom: "{" list "|" list "}" -> general_game
     | up_multiple
     | nimber
     | dyadic_rational
     | integer_game
     | named_game

list: [ expression ("," expression)* ]

named_game: CNAME

integer_game: SIGNED_INT

dyadic_rational: integer "/" "2" ("^" unsigned_integer)?

nimber: "*" unsigned_integer?

up_multiple: "^" unsigned_integer? -> up_multiple
           | "^" unsigned_integer? "*" -> upstar_multiple
           | "v" unsigned_integer? -> down_multiple
           | "v" unsigned_integer? "*" -> downstar_multiple

integer: SIGNED_INT

unsigned_integer: INT

%import common.CNAME
%import common.INT
%import common.SIGNED_INT
%import common.WS
%ignore WS
"""

parser = Lark(grammar, start='statement')

# EVAL

class EvalStatement(Transformer):
    """Transformer to convert parse tree into appropriate actions."""

    def quit_statement(self, items):
        raise Discard

    def unsigned_integer(self, items):
        return int(items[0])

    def integer(self, items):
        return int(items[0])

    def integer_game(self, items):
        return Game.integer(int(items[0]))

    def dyadic_rational(self, items):
        num, *rest = items
        if rest:
            return Game.dyadicRational(int(num), int(rest[0]))
        else:
            return Game.dyadicRational(int(num), 1)

    def nimber(self, items):
        if items:
            return Game.nimber(int(items[0]))
        else:
            return Game.nimber(1)

    def ups(self, items, ud, star):
        """Helper method for up multiples"""
        if items:
            return Game.upMultiple(ud*int(items[0]), star)
        else:
            return Game.upMultiple(ud, star)

    def up_multiple(self, items):
        return self.ups(items, 1, 0)

    def upstar_multiple(self, items):
        return self.ups(items, 1, 1)

    def down_multiple(self, items):
        return self.ups(items, -1, 0)

    def downstar_multiple(self, items):
        return self.ups(items, -1, 1)

    list = list

    def general_game(self, items):
        left, right = items
        return Game.generalGame(left, right)

    def named_game(self, items):
        if items[0] in heap:
            return heap[items[0]]
        else:
            # variable not assigned
            raise GrammarError("Variable " + items[0] + " is not defined.")

    def name(self, items):
        return str(items[0])

    def assignment(self, items):
        heap[items[0]] = items[1]
        return items[1]

    def compare(self, items, lst):
        """Helper method for all comparisons."""
        return any(l == cmpGames(items[0], items[1]) for l in lst)

    def equal_to(self, items):
        return self.compare(items, [0])

    def less_than(self, items):
        return self.compare(items, [-1])

    def greater_than(self, items):
        return self.compare(items, [1])

    def fuzzy_with(self, items):
        return self.compare(items, [2])

    def less_equal(self, items):
        return self.compare(items, [-1,0])

    def greater_equal(self, items):
        return self.compare(items, [1,0])

    def less_fuzzy(self, items):
        return self.compare(items, [-1,2])

    def greater_fuzzy(self, items):
        return self.compare(items, [1,2])

    def sum(self, items):
        if len(items) > 1: # sum + atom
            return items[0] + items[1]
        else: # just atom
            return items[0]

    def negation(self, items):
        return -items[0]

def main_loop():
    exit = False
    while not exit:
            statement = input("CGScript> ")
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
