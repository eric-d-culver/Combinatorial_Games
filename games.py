#!/usr/bin/python3

from functools import lru_cache

test = False

@lru_cache(maxsize=256)
def cmpGames(G,H):
    """returns 0: G == H, 1: G > H, -1: G < H, 2: G || H, Recursive, so caches recent values."""
    goodLeftMove = False
    goodRightMove = False
    for GL in G.LeftOptions:
        cmp = cmpGames(GL,H)
        if cmp is 1 or cmp is 0:
            goodLeftMove = True
    for HR in H.RightOptions:
        cmp = cmpGames(G,HR)
        if cmp is 1 or cmp is 0:
            goodLeftMove = True
    for GR in G.RightOptions:
        cmp = cmpGames(GR,H)
        if cmp is -1 or cmp is 0:
            goodRightMove = True
    for HL in H.LeftOptions:
        cmp = cmpGames(G,HL)
        if cmp is -1 or cmp is 0:
            goodRightMove = True
    if not goodLeftMove and not goodRightMove:
        return 0 # Second player win
    if goodLeftMove and not goodRightMove:
        return 1 # Left player win
    if not goodLeftMove and goodRightMove:
        return -1 # Right player win
    if goodLeftMove and goodRightMove:
        return 2 # First player win # I wish I had a better value than this

def convertNameToNumber(s):
    """converts the name of number-valued games to their number as integer type"""
    lst = s.split('/')
    if len(lst) > 1:
        lst2 = lst[1].split('^')
        if len(lst2) > 1:
            return int(lst[0]) / (int(lst2[0])**int(lst2[1]))
        else:
            return int(lst[0]) / int(lst2[0])
    else:
        return int(lst[0])

@lru_cache(maxsize=256)
def leftStop(g):
    """returns the Left Stop of a game as an integer type"""
    if isNumber(g):
        return convertNameToNumber(g.name)
    else:
        return max(rightStop(l) for l in g.LeftOptions)

@lru_cache(maxsize=256)
def rightStop(g):
    """returns the Right Stop of a game as an integer type"""
    if isNumber(g):
        return convertNameToNumber(g.name)
    else:
        return min(leftStop(r) for r in g.RightOptions)

@lru_cache(maxsize=256)
def isNumber(g):
    """returns True if g is a number. Uses the fact that numbers have all negative incentives."""
    return all(cmpGames(l-g, Game.Integer(0)) == -1 for l in g.LeftOptions) and all(cmpGames(g-r, Game.Integer(0)) == -1 for r in g.RightOptions)

# methods for converting games to canonical form
def dominated(lst, lr):
    """Returns strictly dominated options in lst. lr is 1 for Left, -1 for Right"""
    dominated = []
    for o in lst:
        for oprime in lst:
            if cmpGames(oprime, o) == lr:
                dominated.append(o)
                break
    return dominated

def reversible(left, right):
    """Returns reversible options, and what they reverse too."""
    G = Game(left, right, '{'+','.join(str(l) for l in left)+'|'+','.join(str(r) for r in right)+'}')
    leftReversible = []
    leftReversesTo = []
    rightReversible = []
    rightReversesTo = []
    for GL in G.LeftOptions:
        for GLR in GL.RightOptions:
            c = cmpGames(G, GLR)
            if c == 1 or c == 0:
                leftReversible.append(GL)
                leftReversesTo.extend(GLR.LeftOptions)
                break
    for GR in G.RightOptions:
        for GRL in GR.LeftOptions:
            c = cmpGames(G, GRL)
            if c == -1 or c == 0:
                rightReversible.append(GR)
                rightReversesTo.extend(GRL.RightOptions)
                break
    return leftReversible, leftReversesTo, rightReversible, rightReversesTo

@lru_cache(maxsize=256)
def isNumberish(g):
    """returns True if g is a number plus an infinitesimal"""
    return LeftStop(g) == RightStop(g)

@lru_cache(maxsize=256)
def isInfinitesimal(g):
    """returns True if g is an infinitesimal"""
    return LeftStop(g) == 0 and RightStop(g) == 0


# all of the following methods assume game is in canonical form

@lru_cache(maxsize=256)
def isZero(g):
    """returns True if g is zero"""
    return not g.LeftOptions and not g.RightOptions

def isZeroLists(left, right):
    """Version of isZero when game is not created yet"""
    return not left and not right

@lru_cache(maxsize=256)
def isPositiveInt(g):
    """returns True if g is a positive integer"""
    return not g.RightOptions and all(isPositiveInt(l) or isZero(l) for l in g.LeftOptions)

def isPositiveIntLists(left, right):
    """Version of isPositiveInt when game is not created yet"""
    return not right and all(isPositiveInt(l) or isZero(l) for l in left)

@lru_cache(maxsize=256)
def isNegativeInt(g):
    """returns True if g is a negative integer"""
    return not g.LeftOptions and all(isNegativeInt(r) or isZero(r) for r in g.RightOptions)

def isNegativeIntLists(left, right):
    """Version of isNegativeInt when game is not created yet"""
    return not left and all(isNegativeInt(r) or isZero(r) for r in right)

@lru_cache(maxsize=256)
def isDyadicRational(g):
    """returns True if g is a dyadic rational. Only works for short games."""
    return isNumber(g) and not isZero(g) and not isPositiveInt(g) and not isNegativeInt(g)

def isDyadicRationalLists(left, right):
    """Version of isDyadicRational when game is not created yet"""
    return all(cmpGames(l,r) == -1 for l in left for r in right) and all(isNumber(l) for l in left) and all(isNumber(r) for r in right)  and not isZeroLists(left, right) and not isPositiveIntLists(left, right) and not isNegativeLists(left, right)

@lru_cache(maxsize=256)
def isNimber(g):
    return isNimberLists(g.LeftOptions, g.RightOptions)

def isNimberLists(left, right):
    return len(left) == len(right) and all(isNimber(l) for l in left) and all(isNimber(r) for r in right)

# this implementation is not very memory efficient (for instance *n uses space O(n^2))
# what might be better is to have a dictionary as a class variable with the names as keys
# and a tuple (LeftOptions, RightOptions) as value (where the options are lists of names for games)
# then instances would only store the name of their Game
# and the methods would access this class dictionary
class Game:
    """Combinatorial game class (immutable, hashable)"""
    def __init__(self, LeftOptions, RightOptions, name):
        """Should only be directly invoked when you construct the canonical form of a game"""
        self.LeftOptions = LeftOptions
        self.RightOptions = RightOptions
        self.name = name
        self.nus = False
        self.integer = 0
        self.numerator = 0
        self.denPow = 0
        self.nimber = 0
        self.ups = 0

    def __repr__(self):
        return "< Game object " + self.name + " >"

    def __str__(self):
        return self.name

    def __hash__(self):
        """Provides a hash value for caching results"""
        return hash(self.name)

    def __eq__(self, other):
        """Equality comparison for caching"""
        return hash(self.name) == hash(other.name)

    def __add__(self, other):
        """Addition operator"""
        left = []
        right = []
        for SL in self.LeftOptions:
            left.append(SL + other)
        for OL in other.LeftOptions:
            left.append(self + OL)
        for SR in self.RightOptions:
            right.append(SR + other)
        for OR in other.RightOptions:
            right.append(self + OR);
        return Game.GeneralGame(left, right)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        neg_l = [-r for r in self.RightOptions]
        neg_r = [-l for l in self.LeftOptions]
        if self.name[0] is '-':
            neg_name = self.name[1:]
        else:
            neg_name = '-' + self.name
        return Game(neg_l, neg_r, neg_name)

    def setInteger(self, i):
        self.nus = True
        self.integer = i
        self.numerator = i
        self.denPow = 0
        return

    def setDyadicRational(n,d):
        self.nus = True
        self.numerator = n
        self.denPow = d
        return

    def setNimber(n):
        self.nus = True
        self.nimber = n
        return

    @classmethod
    def Integer(cls, i):
        """Constructor for integer valued games"""
        if i == 0:
            res = cls([], [], '0')
            res.setInteger(0)
            return res 
        if i > 0:
            res = cls([cls.Integer(i-1)], [], str(i))
            res.setInteger(i)
            return res
        if i < 0:
            res = cls([], [cls.Integer(i+1)], str(i))
            res.setInteger(i)
            return res 
    
    @classmethod
    def DyadicRational(cls, num, denPow):
        """Constructor for dyadic rational valued games"""
        if denPow == 0: # denominator is 1
            return cls.Integer(num)
        if (num % 2) == 0: # numerator is even
            return cls.DyadicRational(int(num/2), denPow-1)
        if denPow == 1:
            den = "2"
        else:
            den = "2^" + str(denPow)
        res = cls([cls.DyadicRational(num-1, denPow)], [cls.DyadicRational(num+1, denPow)], str(num) + '/' + den)
        res.setDyadicRational(num, denPow)
        return res

    @classmethod
    def Nimber(cls, i):
        """Constructor for nimber valued games"""
        if i == 0:
            return cls.Integer(0)
        if i == 1:
            num = ''
        else:
            num = str(i)
        lst = []
        for j in range(i):
            lst.append(cls.Nimber(j))
        res = cls(lst, lst, '*' + num)
        res.setNimber(i)
        return res

    @classmethod
    def UpMultiple(cls, n, star):
        """Constructor for multiples of up, with an optional star added"""
        if n == 0:
            return cls.Nimber(star)
        if n == 1 or n == -1:
            num = ''
        elif n < 0:
            num = str(-n)
        else:
            num = str(n)
        if star:
            s = '*'
        else:
            s = ''
        if n == 1 and star == 1:
            res = cls([cls.Integer(0), cls.Nimber(1)], [cls.Integer(0)], '^*')
        if n == -1 and star == 1:
            res = cls([cls.Integer(0)], [cls.Integer(0), cls.Nimber(1)], 'v*')
        if n > 0:
            res = cls([cls.Integer(0)], [cls.UpMultiple(n-1,1-star)], '^' + num + s)
        if n < 0:
            res = cls([cls.UpMultiple(n+1,1-star)], [cls.Integer(0)], 'v' + num + s)
        return res

    @classmethod
    def GeneralGame(cls, left, right):
        """Constructor for general games. Eliminates dominated options, bypasses reversible options, and generates a name"""
        areDominated = True
        areReversible = True
        name = ''
        while areDominated or areReversible:
            # eliminate dominated options
            left = list(dict.fromkeys(left)) # removes duplicates
            right = list(dict.fromkeys(right)) # removes duplicates
            leftDominated = dominated(left, 1)
            rightDominated = dominated(right, -1)
            areDominated = bool(leftDominated) or bool(rightDominated) # false if both lists are empty
            left = [l for l in left if l not in leftDominated]
            right = [r for r in right if r not in rightDominated]
            # bypass reversible options (can we do this without creating a Game?)
            leftReversible, leftReversesTo, rightReversible, rightReversesTo = reversible(left, right)
            areReversible = bool(leftReversible) or bool(rightReversible) # false if both lists are empty
            left = [l for l in left if l not in leftReversible]
            right = [r for r in right if r not in rightReversible]
            left.extend(leftReversesTo)
            right.extend(rightReversesTo)
        # would be nice if common games can be recognized and given the appropriate name
        name = '{' + ','.join(str(l) for l in left) + '|' + ','.join(str(r) for r in right) + '}'
        if isZeroLists(left, right):
            return cls.Integer(0)
        elif isPositiveIntLists(left, right):
            return cls.Integer(left[0].integer + 1)
        elif isNegativeIntLists(left, right):
            return cls.Integer(right[0].integer - 1)
        elif isDyadicRationalLists(left, right):
            return cls.DyadicRational(2*left[0].numerator + 1, left[0].denPow + 1)
        elif isNimberLists(left, right):
            if len(left) == 1:
                name = '*'
            else:
                name = '*' + str(len(left))
        return cls(left, right, name)

if test:
    # dominated options test
    l = [Game.integer(0), Game.integer(0)]
    r = [Game.integer(1), Game.integer(2)]
    g = Game.generalGame(l,r)
    print(cmpGames(g, Game.dyadicRational(1,1)) == 0) # True
    # reversible options test
    i = [Game.nimber(0), Game.nimber(2)]
    h = Game.generalGame(i,i)
    print(cmpGames(h, Game.nimber(1)) == 0) # True
