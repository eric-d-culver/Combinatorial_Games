#/usr/bin/python3

from lark import Lark, Transformer, GrammarError, Discard
from games import Game, cmpGames, heatGame, thermalDecomposition, convertNumberToName

heap = {} # stores variables with assignments. Key is variable name, value is Game variable is assigned to

# READ

# add '#' for +- switches
# add '$' for up squared, up cubed, etc.
# add 'G.U' for Norton Product?
# how to recognize '1/4', and '1/8', etc? Probably keep internal names the same, might convert back and forth when printing

grammar = r"""
?statement: quit_statement 
         | comparison
         | assignment
         | thermal_decomp
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

thermal_decomp: "~" atom

name: CNAME

?expression: term
           | additive_expression

additive_expression: additive_expression "+" term -> sum
                   | additive_expression "-" term -> difference
                   | term

?term: atom
     | "-" atom -> negation
     | "$" atom "@" atom -> heating

?atom: "{" list "|" list "}" -> general_game
     | nus
     | named_game
     | "(" expression ")"

list: [ expression ("," expression)* ]

?nus: dyadic_rational
    | integer_game
    | nimber
    | up_mult_num nimber_num? -> up_star
    | number nimber_num -> number_star
    | number up_mult_num nimber_num? -> number_up_star

number: integer
      | integer "/" "2" ("^" unsigned_integer)? -> fraction

?up_mult_num: "^" unsigned_integer? -> up_mult_num
            | "v" unsigned_integer? -> down_mult_num

nimber_num: "*" unsigned_integer?

named_game: CNAME

integer_game: SIGNED_INT

dyadic_rational: integer "/" "2" ("^" unsigned_integer)?

nimber: "*" unsigned_integer?

up_multiple: "^" unsigned_integer? -> up_multiple
           | "v" unsigned_integer? -> down_multiple

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

def debug(name, items):
    if False:
        print(name, ' ', items)

class EvalStatement(Transformer):
    """Transformer to convert parse tree into appropriate actions."""

    def quit_statement(self, items):
        debug('quit', items)
        raise Discard

    def thermal_decomp(self, items):
        res = ""
        decomp = thermalDecomposition(items[0])
        for inf, temp in decomp[:-1]: # last element of decomp is mean value
            res += "$" + convertNumberToName(temp) + "@" + str(inf) + " + " # could be prettier
        res += str(decomp[-1][0])
        return res

    def unsigned_integer(self, items):
        debug('unsigned_integer', items)
        return int(items[0])

    def integer(self, items):
        debug('integer', items)
        return int(items[0])

    def fraction(self, items):
        debug('fraction', items)
        if len(items) > 1:
            return (int(items[0]), int(items[1])) # integer / 2 ^ unsigned_integer
        else:
            return (int(items[0]), 1) # integer / 2

    def number(self, items):
        debug('number', items)
        return (int(items[0]), 0) # integer

    def up_mult_num(self, items):
        debug('up_mult_num', items)
        if len(items) > 0:
            return int(items[0])
        else:
            return 1

    def down_mult_num(self, items):
        debug('down_mult_num', items)
        if len(items) > 0:
            return -int(items[0])
        else:
            return -1

    def nimber_num(self, items):
        debug('nimber_num', items)
        if len(items) > 0:
            return int(items[0])
        else:
            return 1

    def number_up_star(self, items):
        debug('number_up_star', items)
        if len(items) > 2:
            return Game.NumberUpStar(int(items[0][0]), int(items[0][1]), int(items[1]), int(items[2]))
        else: 
            return Game.NumberUpStar(int(items[0][0]), int(items[0][1]), int(items[1]), 0)

    def number_star(self, items):
        debug('number_star', items)
        return Game.NumberStar(int(items[0][0]), int(items[0][1]), int(items[1]))

    def up_star(self, items):
        debug('up_star', items)
        if len(items) == 2:
            return Game.UpMultiple(int(items[0]), int(items[1]))
        else:
            return Game.UpMultiple(int(items[0]), 0)

    def integer_game(self, items):
        return Game.Integer(int(items[0]))

    def dyadic_rational(self, items):
        num, *rest = items
        if rest:
            return Game.DyadicRational(int(num), int(rest[0]))
        else:
            return Game.DyadicRational(int(num), 1)

    def nimber(self, items):
        debug('nimber', items)
        if items:
            return Game.Nimber(int(items[0]))
        else:
            return Game.Nimber(1)

    def ups(self, items, ud, star):
        """Helper method for up multiples"""
        if items:
            return Game.UpMultiple(ud*int(items[0]), star)
        else:
            return Game.UpMultiple(ud, star)

    def up_multiple(self, items):
        debug('up_multiple', items)
        return self.ups(items, 1, 0)

    def down_multiple(self, items):
        debug('down_multiple', items)
        return self.ups(items, -1, 0)

    list = list

    def general_game(self, items):
        left, right = items
        return Game.GeneralGame(left, right)

    def named_game(self, items):
        debug('named_game', items)
        if str(items[0]) in heap:
            return heap[str(items[0])]
        else:
            # variable not assigned
            raise GrammarError("Variable " + str(items[0]) + " is not defined.")

    def name(self, items):
        debug('name', items)
        return str(items[0])

    def assignment(self, items):
        debug('assignment', items)
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

    def additive_expression(self, items):
        return items[0]

    def sum(self, items):
        debug('sum', items)
        if len(items) > 1: # sum + atom
            return items[0] + items[1]
        else: # atom
            return items[0]

    def difference(self, items):
        debug('difference', items)
        if len(items) > 1: # difference - atom
            return items[0] - items[1]
        else: # atom
            return items[0]

    def negation(self, items):
        debug('negation', items)
        return -items[0]

    def heating(self, items):
        debug('heating', items)
        return heatGame(items[1], items[0])

