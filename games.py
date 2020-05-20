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
        if denPow == 0: # denominator is 1
            return cls.integer(num)
        if (num % 2) == 0: # numerator is even
            return cls.dyadicRational(int(num/2), denPow-1)
        if denPow == 1:
            den = "2"
        else:
            den = "2^" + str(denPow)
        return cls([cls.dyadicRational(num-1, denPow)], [cls.dyadicRational(num+1, denPow)], str(num) + '/' + den)

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
        if n > 0:
            return cls([cls.integer(0)], [cls.upMultiple(n-1,1-star)], '^' + num + s)
        if n < 0:
            return cls([cls.upMultiple(n+1,1-star)], [cls.integer(0)], 'v' + num + s)
        pass

    @classmethod
    def generalGame(cls, left, right):
        """Constructor for general games. Eliminates dominated options, bypasses reversible options, and generates a name"""
        areDominated = True
        areReversible = True
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
        return cls(left, right, '{' + ', '.join(str(l) for l in left) + '|' + ', '.join(str(r) for r in right) + '}')

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
