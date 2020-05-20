#!/usr/bin/python3

from lark import Lark, Transformer
import games

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
          | integer
          | dyadic_rational
          | nimber
          | up_multiple

list: [ expression ("," expression)* ]

integer: SIGNED_INT

dyadic_rational: integer "/" "2" ("^" unsigned_integer)?

nimber: "*" unsigned_integer?

up_multiple: "^" unsigned_integer -> up_multiple
           | "^" unsigned_integer "*" -> upstar_multiple
           | "v" unsigned_integer -> down_multiple
           | "v" unsigned_integer "*" -> downstar_multiple

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

    def unsigned_integer(self, i):
        return i

    def integer(self, i):
        return Game.integer(i)

    def dyadic_rational(self, items):
        num, rest* = items
        if rest:
            return Game.dyadicRational(num, rest[0])
        else:
            return Game.dyadicRational(num, 1)

    def nimber(self, i):
        if i:
            return Game.nimber(i)
        else:
            return Game.nimber(1)

    def up_multiple(self, i):
        if i:
            return Game.upMultiple(i, 0)
        else:
            return Game.upMultiple(1, 0)

    def upstar_multiple(self, i):
        if i:
            return Game.upMultiple(i, 1)
        else:
            return Game.upMultiple(1, 1)

    def down_multiple(self, i):
        if i:
            return Game.upMultiple(-i, 0)
        else:
            return Game.upMultiple(-1, 0)

    def downstar_multiple(self, i):
        if i:
            return Game.upMultiple(i, 1)
        else:
            return Game.upMultiple(1, 1)

    def list(self, items):
        return list(items)

    def general_game(self, items):
        left, right = items
        return Game.generalGame(left, right)

if test:
    tree = parser,parse("{0, ^2*,  *17|  1, *}")
    print(tree.pretty())
    print(EvalStatement().transform(tree))
