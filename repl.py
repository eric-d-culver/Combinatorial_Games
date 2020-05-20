#!/usr/bin/python3

from lark import Lark, Transformer
from games import Game

test = True

# READ

grammar = r"""
?statement: comparison
         | assignment
         | expression

comparison: expression "=" expression -> equal_to
          | expression "<" expression -> less_than
          | expression ">" expression -> greater_than
          | expression "<>" expression -> fuzzy_with
          | expression "<=" expression -> less_equal
          | expression ">=" expression -> greater_equal
          | expression "<|" expression -> less_fuzzy
          | expression "|>" expression -> greater_fuzzy

assignment: name ":=" expression

name: CNAME

?expression: "{" list "|" list "}" -> general_game
          | integer_game
          | dyadic_rational
          | nimber
          | up_multiple

list: [ expression ("," expression)* ]

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

    def up_multiple(self, items):
        if items:
            return Game.upMultiple(int(items[0]), 0)
        else:
            return Game.upMultiple(1, 0)

    def upstar_multiple(self, items):
        if items:
            return Game.upMultiple(int(items[0]), 1)
        else:
            return Game.upMultiple(1, 1)

    def down_multiple(self, items):
        if items:
            return Game.upMultiple(-int(items[0]), 0)
        else:
            return Game.upMultiple(-1, 0)

    def downstar_multiple(self, items):
        if items:
            return Game.upMultiple(-int(items[0]), 1)
        else:
            return Game.upMultiple(-1, 1)

    list = list

    def general_game(self, items):
        print(items)
        left, right = items
        return Game.generalGame(left, right)

if test:
    tree = parser.parse("{0, ^2*,  *17|  1/2^2, 1, v, *}")
    print(tree.pretty())
    print(EvalStatement().transform(tree))
