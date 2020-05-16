#!/usr/bin/python3

from functools import lru_cache


@lru_cache(maxsize=256)
def cmpGames(G,H):
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

class Game:
    """Combinatorial game class (immutable, hashable)"""
    def __init__(self, LeftOptions, RightOptions, name):
        """Should only be directly invoked when you construct the canonical form of a game"""
        self.LeftOptions = LeftOptions
        self.RightOptions = RightOptions
        self.name = name

    def __hash__(self):
        """Provides a hash value for caching results"""
        return hash(self.name)

    def __add__(self, other):
        pass

    @classmethod
    def integer(cls, i):
        """Constructor for integer valued games"""
        if i == 0:
            return cls([],[],"0")
        if i > 0:
            return cls([cls.integer(i-1)],[],str(i))
        if i < 0:
            return cls([],[cls.integer(i+1)],str(i))
    
    @classmethod
    def dyadicRational(cls, num, denPow):
        """Constructor for dyadic rational valued games"""
        if num % 2 == 0: # numerator is even
            return cls.dyadicRational(num/2, denPow-1)
        if denPow == 0: # denominator is 1
            return cls.integer(num)
        return cls([cls.dyadicRational(num-1, denPow)],[cls.dyadicRational(num+1, denPow)],str(num)+'/'+'2^'+str(denPow))

    @classmethod
    def nimber(cls, i):
        """Constructor for nimber valued games"""
        if i == 0:
            return cls.integer(0)
        lst = []
        for j in range(i):
            lst.append(cls.nimber(j))
        return cls(lst, lst, "*"+str(i))
