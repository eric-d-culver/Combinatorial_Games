#!/usr/bin/python3

from functools import lru_cache

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

def removeDominated(lst, lr):
    """Returns lst with dominated options removed. lr is 1 for Left, -1 for Right"""
    dominated = []
    for o in lst:
        for oprime in lst:
            if cmpGames(oprime, o) == lr:
                dominated.append(o)
                break
    return [o for o in lst if o not in dominated]

def bypassReversible(left, right, lr):
    pass

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

    def __repr__(self):
        return "< Game object " + self.name + " >"

    def __str__(self):
        return self.name

    def __hash__(self):
        """Provides a hash value for caching results"""
        return hash(self.name)

    def __eq__(self, other):
        """Equality comparison"""
        return cmpGames(self, other) == 0

    def __lt__(self, other):
        """Less than comparison"""
        return cmpGames(self, other) == -1

    def __gt__(self, other):
        """Greater than comparison"""
        return cmpGames(self, other) == 1

    def __le__(self, other):
        """Less than or equal to comparison"""
        c = cmpGames(self, other)
        return c == -1 or c == 0

    def __ge__(self, other):
        """Greater than or equal to comparison"""
        c = cmpGames(self, other)
        return c == 1 or c == 0

    def __ne__(Self, other):
        """Fuzzy comparison""" # is this allowed? What might break?
        return cmpGames(self, other) == 2

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
        return Game.generalGame(left, right)

    @classmethod
    def integer(cls, i):
        """Constructor for integer valued games"""
        if i == 0:
            return cls([], [], '0')
        if i > 0:
            return cls([cls.integer(i-1)], [], str(i))
        if i < 0:
            return cls([], [cls.integer(i+1)], str(i))
    
    @classmethod
    def dyadicRational(cls, num, denPow):
        """Constructor for dyadic rational valued games"""
        if num % 2 == 0: # numerator is even
            return cls.dyadicRational(num/2, denPow-1)
        if denPow == 0: # denominator is 1
            return cls.integer(num)
        return cls([cls.dyadicRational(num-1, denPow)], [cls.dyadicRational(num+1, denPow)], str(num) + '/' + "2^" + str(denPow))

    @classmethod
    def nimber(cls, i):
        """Constructor for nimber valued games"""
        if i == 0:
            return cls.integer(0)
        if i == 1:
            num = ''
        else:
            num = str(i)
        lst = []
        for j in range(i):
            lst.append(cls.nimber(j))
        return cls(lst, lst, '*' + num)

    @classmethod
    def upMultiple(cls, n, star):
        """Constructor for multiples of up, with an optional star added"""
        if n == 0:
            return cls.nimber(star)
        if n == 1:
            num = ''
        else:
            num = str(n)
        if star:
            s = ''
        else:
            s = '*'
        if n > 0:
            return cls([0], [cls.upMultiple(n-1,1-star)], '^' + num + s)
        if n < 0:
            return cls([cls.upMultiple(n+1,1-star)], [0], 'v' + num + s)
        pass

    @classmethod
    def generalGame(cls, left, right):
        """Constructor for general games. Eliminates dominated options, bypasses reversible options, and generates a name"""
        # eliminate dominated options
        left = removeDominated(left, 1)
        right = removedDominated(right, -1)
        # bypass reversible options (can we do this without creating a Game?)
        # would be nice if common games can be recognized and given the appropriate name
        return cls(left, right, '{' + ', '.join(left) + '|' + ', '.join(right) + '}')
