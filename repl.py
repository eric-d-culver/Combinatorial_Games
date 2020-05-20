#!/usr/bin/python3

from lark import Lark, Transformer
from games import Game, cmpGames

test = True

heap = {} # stores variables with assignments. Key is variable name, value is Game variable is assigned to

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

    def ups(self, items, ud, star):
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

    def name(self, items):
        return str(items[0])

    def assignment(self, items):
        heap[items[0]] = items[1]
        return items[1]

    def compare(self, items, lst):
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

if test:
    tree = parser.parse("g := {0, ^2*,  *17|  1/2^2, 1, v, *}")
    print(tree.pretty())
    print(EvalStatement().transform(tree))
    print(heap['g'])
