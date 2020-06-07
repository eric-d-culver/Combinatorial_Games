#!/usr/bin/python3

from functools import lru_cache
from collections import Counter

test = False

@lru_cache(maxsize=256)
def cmpGames(G,H):
    """returns 0: G == H, 1: G > H, -1: G < H, 2: G || H, Recursive, so caches recent values."""
    #print(G.name, ' ', H.name)
    goodLeftMove = False
    goodRightMove = False
    for GL in G.LeftOptions:
        #print('Calling: ', GL, ' ', H)
        cmp = cmpGames(GL,H)
        if cmp is 1 or cmp is 0:
            goodLeftMove = True
            break
    for HR in H.RightOptions:
        #print('Calling: ', G, ' ', HR)
        cmp = cmpGames(G,HR)
        if cmp is 1 or cmp is 0:
            goodLeftMove = True
            break
    #print('Good Left Move: ', goodLeftMove)
    for GR in G.RightOptions:
        #print('Calling: ', GR, ' ', H)
        cmp = cmpGames(GR,H)
        if cmp is -1 or cmp is 0:
            goodRightMove = True
            break
    for HL in H.LeftOptions:
        #print('Calling: ', G, ' ', HL)
        cmp = cmpGames(G,HL)
        if cmp is -1 or cmp is 0:
            goodRightMove = True
            break
    #print('Good Right Move: ', goodRightMove)
    if not goodLeftMove and not goodRightMove:
        #print('Value: 0')
        return 0 # Second player win
    if goodLeftMove and not goodRightMove:
        #print('Value: 1')
        return 1 # Left player win
    if not goodLeftMove and goodRightMove:
        #print('Value: -1')
        return -1 # Right player win
    if goodLeftMove and goodRightMove:
        #print('Value: 2')
        return 2 # First player win # I wish I had a better value than this

@lru_cache(maxsize=256)
def addGames(G, H):
    left = []
    right = []
    for GL in G.LeftOptions:
        left.append(GL + H)
    for HL in H.LeftOptions:
        left.append(G + HL)
    for GR in G.RightOptions:
        right.append(GR + H)
    for HR in H.RightOptions:
        right.append(G + HR);
    return Game.GeneralGame(left, right)

@lru_cache(maxsize=256)
def heatGame(G, H):
    if isNumber(G):
        return G
    else:
        left = [heatGame(l, H) + H for l in G.LeftOptions]
        right = [heatGame(r, H) - H for r in G.RightOptions]
        return Game.GeneralGame(left, right)

@lru_cache(maxsize=256)
def overcool(G, H):
    """Cools G by H without worry about past phase transitions"""
    if isNumber(G):
        return G
    else:
        left = [overcool(l, H) - H for l in G.LeftOptions]
        right = [overcool(r, H) + H for r in G.RightOptions]
        return Game.GeneralGame(left, right)

@lru_cache(maxsize=256)
def thermalDecomposition(G):
    """returns a list of tuples giving the infinitesimals emitted by G as it cools, and the temperatures at which they are emitted."""
    decomp = []
    if isNumber(G):
        return [(G, 0)]
    while not isNumber(G):
        #print('G ', G)
        denPow = 0 
        num = 0 # num/2^denPow is total temperature cooled
        tempA = tempB = G
        while not (isNumberish(tempB) and not isNumber(tempB)):
            #print('temp ', num/(2**denPow))
            #print('step ', 2**(-denPow))
            #print('tempA ', tempA)
            #print('tempB ', tempB)
            if isNumber(tempB):
                #print('tempB is number, temp ', num/(2**denPow))
                tempB = tempA
                num -= 1 # temp goes back by step size
                denPow += 1 
                num *= 2 # reduce step size in half
                #print('temp now ', num/(2**denPow))
            else:
                #print('tempB is not a number, temp ', num/(2**denPow))
                num += 1 # increase temperature by step size
                tempA = tempB
                tempB = overcool(tempA, Game.DyadicRational(1, denPow))
        number = convertNumberToGame(numberPart(tempB))
        inf = tempB - number
        #print('tempB freezes as ', tempB)
        #print('inf ', inf)
        #print('temp ', num/(2**denPow))
        G -= heatGame(inf, Game.DyadicRational(num, denPow))
        decomp.append((inf, num/(2**denPow)))
    decomp.append((G, num/(2**denPow)))
    return decomp

@lru_cache(maxsize=256)
def convertNumberToGame(n):
    """converts dyadic rational to game. Will loop infinitely if given any other number"""
    denPow = 0
    while n % 1 != 0:
        denPow += 1
        n *= 2
    return Game.DyadicRational(int(n), denPow)

@lru_cache(maxsize=256)
def convertNumberToName(n):
    """converts dyadic rational to internal name. Will loop infinitely if given any other number"""
    denPow = 0
    while n % 1 != 0:
        denPow += 1
        n *= 2
    n = int(n)
    if denPow == 0:
        return str(n)
    elif denPow == 1:
        return str(n) + "/2"
    else:
        return str(n) + "/2^" + str(denPow)

@lru_cache(maxsize=256)
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
def LeftStop(g):
    """returns the Left Stop of a game as an integer type"""
    if isNumber(g):
        return convertNameToNumber(g.name)
    else:
        return max(RightStop(l) for l in g.LeftOptions)

@lru_cache(maxsize=256)
def RightStop(g):
    """returns the Right Stop of a game as an integer type"""
    if isNumber(g):
        return convertNameToNumber(g.name)
    else:
        return min(LeftStop(r) for r in g.RightOptions)

@lru_cache(maxsize=256)
def isNumber(g):
    """returns True if g is a number. Uses the fact that numbers have all negative incentives."""
    return all(cmpGames(l, g) == -1 for l in g.LeftOptions) and all(cmpGames(g, r) == -1 for r in g.RightOptions)

@lru_cache(maxsize=256)
def isNumberish(g):
    """returns True if g is a number plus an infinitesimal"""
    return LeftStop(g) == RightStop(g)

@lru_cache(maxsize=256)
def isInfinitesimal(g):
    """returns True if g is an infinitesimal"""
    return LeftStop(g) == 0 and RightStop(g) == 0

@lru_cache(maxsize=256)
def numberPart(g):
    """returns number g is infinitesimally close to, raises error if g is not Numberish"""
    if isNumberish(g):
        return LeftStop(g)
    else:
        raise Error

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
                #print(GL, ' reverses to ', GLR)
                leftReversible.append(GL)
                leftReversesTo.extend(GLR.LeftOptions)
                break
    for GR in G.RightOptions:
        for GRL in GR.LeftOptions:
            c = cmpGames(G, GRL)
            if c == -1 or c == 0:
                #print(GR, ' reverses to ', GRL)
                rightReversible.append(GR)
                rightReversesTo.extend(GRL.RightOptions)
                break
    return leftReversible, leftReversesTo, rightReversible, rightReversesTo

# all of the following methods assume game is in canonical form

def extractNumDen(name):
    """extracts the numerator and denominator power from a dyadic rational name."""
    lst = name.split('/')
    if len(lst) > 1:
        lst2 = lst[1].split('^')
        if len(lst2) > 1:
            denPow = int(lst2[1])
        else:
            denPow = 1
    else:
        denPow = 0
    return (int(lst[0]), denPow)

def extractNumberUpStar(name):
    """extracts the number, up multiple, and nimber value from a number_up_star name"""
    lst = name.split('^')
    if len(lst) == 1:
        lst = name.split('v')
        if len(lst) == 1: # number star
            lst = name.split('*')
            if len(lst) == 1: # number
                return (name, 0, 0)
            elif lst[1] == '': # number *
                return (lst[0], 0, 1)
            else:
                return (lst[0], 0, int(lst[1]))
        else:
            lst2 = lst[1].split('*')
            if len(lst2) == 1 and lst2[0] == '': # number v
                return (lst[0], -1, 0)
            elif len(lst2) == 1: # number down
                return (lst[0], -int(lst2[0]), 0)
            elif lst2[0] == '' and lst2[1] == '': # number v*
                return (lst[0], -1, 1)
            elif lst2[0] == '': # number v star
                return (lst[0], 1, int(lst2[1]))
            elif lst2[1] == '': # number down *
                return (lst[0], -int(lst2[0]), 1)
            else: # number down star
                return (lst[0], -int(lst2[0]), int(lst2[1]))
    else:
        lst2 = lst[1].split('*')
        if len(lst2) == 1 and lst2[0] == '': # number ^
            return (lst[0], 1, 0)
        elif len(lst2) == 1: # number up
            return (lst[0], int(lst2[0]), 0)
        elif lst2[0] == '' and lst2[1] == '': # number ^*
            return (lst[0], 1, 1)
        elif lst2[0] == '': # number ^ star
            return (lst[0], 1, int(lst2[1]))
        elif lst2[1] == '': # number up *
            return (lst[0], int(lst2[0]), 1)
        else: # number up star
            return (lst[0], int(lst2[0]), int(lst2[1]))

def generateName(left, right):
    name = '{' + ','.join(str(l) for l in left) + '|' + ','.join(str(r) for r in right) + '}' # default name if nothing else comes up
    if not left and not right: # zero
        return '0'
    elif not right:  # positive integer
        return str(int(left[0].name) + 1)
    elif not left: # negative integer
        return str(int(right[0].name) - 1)
    elif len(left) == 1 and len(right) == 1 and isNumber(left[0]) and isNumber(right[0]) and cmpGames(left[0], right[0]) == -1: # dyadic rational
        leftNum, leftDenPow = extractNumDen(left[0].name)
        rightNum, rightDenPow = extractNumDen(right[0].name)
        if leftDenPow >= rightDenPow:
            denPow = leftDenPow + 1
            num = 2*leftNum + 1
        else:
            denPow = rightDenPow + 1
            num = 2*rightNum - 1
        if denPow == 1:
            return str(num) + '/' + '2'
        else:
            return str(num) + '/' + '2^' + str(denPow)
    elif isNumberUpStar(Game(left, right, name)):
        if len(left) == 2: # n^*
            if right[0].name == '0':
                return '^*'
            else:
                return right[0].name + '^*'
        else:
            number, ups, stars = extractNumberUpStar(right[0].name)
            if number == '0':
                number = ''
            if ups == 0 and stars == 1:
                return number + '^'
            elif ups == 0: # stars != 0 since that was taken care of above
                return number + '^*' + str(stars^1)
            elif stars == 1:
                return number + '^' + str(ups+1)
            elif stars == 0:
                return number + '^' + str(ups+1) + '*'
            else:
                return number + '^' + str(ups+1) + '*' + str(stars^1)
    elif isNumberDownStar(Game(left, right, name)):
        if len(right) == 2: # nv*
            if left[0].name == '0':
                return 'v*'
            else:
                return left[0].name + 'v*'
        else:
            number, ups, stars = extractNumberUpStar(left[0].name)
            if number == '0':
                number = ''
            if ups == 0 and stars == 1:
                return number + 'v'
            elif ups == 0: # stars != 0 since that was taken care of above
                return number + 'v*' + str(stars^1)
            elif stars == 1:
                return number + 'v' + str(-ups+1)
            elif stars == 0:
                return number + 'v' + str(-ups+1) + '*'
            else:
                return number + 'v' + str(-ups+1) + '*' + str(stars^1)
    elif isNumberStar(Game(left, right, name)):
        if len(left) == 1 and isNumber(left[0]): # {n|n} = n*
            if left[0].name == '0':
                return '*'
            else:
                return left[0].name + '*'
        else:
            star = max(extractNumberUpStar(l.name)[2] for l in left) + 1
            number = extractNumberUpStar(left[0].name)[0]
            if number == '0':
                return '*' + str(star)
            else:
                return number + '*' + str(star)
    else:
        return name

@lru_cache(maxsize=256)
def isZero(g):
    """returns True if g is zero"""
    return not g.LeftOptions and not g.RightOptions

@lru_cache(maxsize=256)
def isPositiveInt(g):
    """returns True if g is a positive integer"""
    return not g.RightOptions and g.LeftOptions

@lru_cache(maxsize=256)
def isNegativeInt(g):
    """returns True if g is a negative integer"""
    return not g.LeftOptions and g.RightOptions

@lru_cache(maxsize=256)
def isDyadicRational(g):
    """returns True if g is a dyadic rational."""
    return len(g.LeftOptions) == 1 and len(g.RightOptions) == 1 and isNumber(g.LeftOptions[0]) and isNumber(g.RightOptions[0]) and cmpGames(g.LeftOptions[0], g.RightOptions[0]) == -1

@lru_cache(maxsize=256)
def isNumberStar(g):
    """returns True if g is a number plus a nimber"""
    if isNumber(g):
        return True
    elif not isNumberish(g):
        return False
    elif isNumberish(g.LeftOptions[0]):
        number = numberPart(g.LeftOptions[0])
        return Counter(g.LeftOptions) == Counter(g.RightOptions) and all(isNumberStar(l) for l in g.LeftOptions) and all(numberPart(l) == number for l in g.LeftOptions) # only need to check left since first part guarentees right is identical
    else:
        return False

@lru_cache(maxsize=256)
def isNumberUpStar(g):
    """returns True if g is a number plus a positive number of ups plus a nimber"""
    if len(g.LeftOptions) == 2 and len(g.RightOptions) == 1 and isNumber(g.RightOptions[0]) and cmpGames(g.LeftOptions[0], g.RightOptions[0]) == 0 and isNumberStar(g.LeftOptions[1]) and numberPart(g.LeftOptions[0]) == numberPart(g.LeftOptions[1]): # {n,n*|n} = n^*
        return True
    elif len(g.LeftOptions) == 2 and len(g.RightOptions) == 1 and isNumber(g.RightOptions[0]) and cmpGames(g.LeftOptions[1], g.RightOptions[0]) == 0 and isNumberStar(g.LeftOptions[0]) and numberPart(g.LeftOptions[0]) == numberPart(g.LeftOptions[1]): # {n*,n|n} = n^*
        return True
    elif len(g.LeftOptions) == 1 and len(g.RightOptions) == 1 and isNumber(g.LeftOptions[0]) and isNumberStar(g.RightOptions[0]) and not isNumber(g.RightOptions[0]) and numberPart(g.LeftOptions[0]) == numberPart(g.RightOptions[0]):
        return True
    return len(g.LeftOptions) == 1 and len(g.RightOptions) == 1 and isNumber(g.LeftOptions[0]) and isNumberUpStar(g.RightOptions[0]) and not isNumber(g.RightOptions[0]) and numberPart(g.RightOptions[0]) == numberPart(g.LeftOptions[0]) # all other cases

@lru_cache(maxsize=256)
def isNumberDownStar(g):
    if len(g.RightOptions) == 2 and len(g.LeftOptions) == 1 and isNumber(g.LeftOptions[0]) and cmpGames(g.RightOptions[0], g.LeftOptions[0]) == 0 and isNumberStar(g.RightOptions[1]) and numberPart(g.RightOptions[0]) == numberPart(g.RightOptions[1]): # {n|n,n*} = nv*
        return True
    elif len(g.RightOptions) == 2 and len(g.LeftOptions) == 1 and isNumber(g.LeftOptions[0]) and cmpGames(g.RightOptions[1], g.LeftOptions[0]) == 0 and isNumberStar(g.RightOptions[0]) and numberPart(g.RightOptions[0]) == numberPart(g.RightOptions[1]): # {n|n*,n} = nv*
        return True
    elif len(g.RightOptions) == 1 and len(g.LeftOptions) == 1 and isNumber(g.RightOptions[0]) and isNumberStar(g.LeftOptions[0]) and not isNumber(g.LeftOptions[0]) and numberPart(g.RightOptions[0]) == numberPart(g.LeftOptions[0]): # {n*|n} = nv
        return True
    return len(g.RightOptions) == 1 and len(g.LeftOptions) == 1 and isNumber(g.RightOptions[0]) and isNumberDownStar(g.LeftOptions[0]) and not isNumber(g.LeftOptions[0]) and numberPart(g.LeftOptions[0]) == numberPart(g.RightOptions[0]) # all other cases
    pass

@lru_cache(maxsize=256)
def isNimber(g):
    """returns True if g is a nimber"""
    return isNimberLists(g.LeftOptions, g.RightOptions) # better way to do this?

def isNimberLists(left, right):
    """Version of isNimber when game is not created yet"""
    return Counter(left) == Counter(right) and all(isNimber(l) for l in left) and all(isNimber(r) for r in right)

def extractNimberNum(name):
    if len(name) > 1:
        return int(name[1:]) # strip '*' off front of name
    elif name[0] == '*':
        return 1
    else:
        return 0

def checkNimberName(left, right):
    """checks if uncreated game is a nimber, and returns the right name if so"""
    if isNimberLists(left, right):
        num = max(extractNimberNum(l.name) for l in left) + 1
        if num == 1:
            return '*', True
        else:
            return '*' + str(num), True
    else:
        return '', False

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
        return addGames(self, other)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        neg_l = [-r for r in self.RightOptions]
        neg_r = [-l for l in self.LeftOptions]
        return Game.GeneralGame(neg_l, neg_r)
        ## neg_name needs to be more complicated -^ = v, etc.
        #if self.name[0] is '-':
            #neg_name = self.name[1:]
        #else:
            #neg_name = '-' + self.name
        #return Game(neg_l, neg_r, neg_name)

    @classmethod
    def Integer(cls, i):
        """Constructor for integer valued games"""
        if i == 0:
            return cls([], [], '0')
        if i > 0:
            return cls([cls.Integer(i-1)], [], str(i))
        if i < 0:
            return cls([], [cls.Integer(i+1)], str(i))
    
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
        return cls([cls.DyadicRational(num-1, denPow)], [cls.DyadicRational(num+1, denPow)], str(num) + '/' + den)

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
        return cls(lst, lst, '*' + num)

    @classmethod
    def UpMultiple(cls, n, star):
        """Constructor for multiples of up, with an optional nimber added"""
        if n == 0:
            return cls.Nimber(star)
        if n == 1:
            upName = '^'
        elif n == -1:
            upName = 'v'
        elif n < 0:
            upName = 'v' + str(-n)
        else:
            upName = '^' + str(n)
        if star == 1:
            sName = '*'
        elif star > 1:
            sName = '*' + str(star)
        else:
            sName = ''
        if n == 1 and star == 1:
            res = cls([cls.Integer(0), cls.Nimber(1)], [cls.Integer(0)], '^*')
        elif n == -1 and star == 1:
            res = cls([cls.Integer(0)], [cls.Integer(0), cls.Nimber(1)], 'v*')
        elif n > 0:
            res = cls([cls.Integer(0)], [cls.UpMultiple(n-1,star^1)], upName + sName)
        elif n < 0:
            res = cls([cls.UpMultiple(n+1,star^1)], [cls.Integer(0)], upName + sName)
        return res

    @classmethod
    def NumberStar(cls, num, denPow, star):
        """Constructor for a number, plus some nimber"""
        number = cls.DyadicRational(num, denPow)
        if number.name == '0':
            numName = ''
        else:
            numName = number.name
        if star == 0:
            return number
        if star == 1:
            name = numName + '*'
        else:
            name = numName + '*' + str(star)
        lst = []
        for j in range(star):
            lst.append(cls.NumberStar(num, denPow, j))
        return cls(lst, lst, name)

    @classmethod
    def NumberUpStar(cls, num, denPow, ups, star):
        """Constructor for a number, plus some number of ups, plus some nimber"""
        number = cls.DyadicRational(num, denPow)
        if number.name == '0':
            numName = ''
        else:
            numName = number.name
        if ups == 0 and star == 0:
            return number
        elif ups == 0:
            return cls.NumberStar(num, denPow, star)
        if ups == 1:
            upName = '^'
        elif ups == -1:
            upName = 'v'
        elif ups > 0:
            upName = '^' + str(ups)
        elif ups < 0:
            upName = 'v' + str(-ups)
        if star == 0:
            starName = ''
        elif star == 1:
            starName = '*'
        else:
            starName = '*' + str(star)
        name = numName + upName + starName
        if ups == 1 and star == 1:
            return cls([number, cls.NumberStar(num, denPow, 1)], [number], name)
        if ups == -1 and star == 1:
            return cls([number], [number, cls.NumberStar(num, denPow, 1)], name)
        if ups > 0:
            return cls([number], [cls.NumberUpStar(num, denPow, ups-1, star^1)], name)
        if ups < 0:
            return cls([cls.NumberUpStar(num, denPow, ups+1, star^1)], [number], name)


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
            #print('Dominated: ', leftDominated, ' ', rightDominated)
            areDominated = bool(leftDominated) or bool(rightDominated) # false if both lists are empty
            left = [l for l in left if l not in leftDominated]
            right = [r for r in right if r not in rightDominated]
            # bypass reversible options (can we do this without creating a Game?)
            leftReversible, leftReversesTo, rightReversible, rightReversesTo = reversible(left, right)
            #print('Reversible: ', leftReversible, ' ', rightReversible)
            #print('To: ', leftReversesTo, ' ', rightReversesTo)
            areReversible = bool(leftReversible) or bool(rightReversible) # false if both lists are empty
            left = [l for l in left if l not in leftReversible]
            right = [r for r in right if r not in rightReversible]
            left.extend(leftReversesTo)
            right.extend(rightReversesTo)
        # recognizes common games and gives them the appropriate name
        name = generateName(left, right)
        return cls(left, right, name)

if test:
    g = Game([Game.UpMultiple(1,1)],[Game.Nimber(1)],'{^*|*}')
    print(cmpGames(g, Game.Integer(0)))
    # dominated options test
    #l = [Game.Integer(0), Game.Integer(0)]
    #r = [Game.Integer(1), Game.Integer(2)]
    #g = Game.GeneralGame(l,r)
    #print(g.name) # 1/2
    #print(cmpGames(g, Game.DyadicRational(1,1)) == 0) # True
    # reversible options test
    #i = [Game.Nimber(0), Game.Nimber(2)]
    #h = Game.GeneralGame(i,i)
    #print(h.name) # *
    #print(cmpGames(h, Game.Nimber(1)) == 0) # True
    #l = [Game.UpMultiple(1,1)]
    #r = [Game.UpMultiple(0,1)]
    #k = Game.GeneralGame(l,r)
    #print(k.name)
    #print(cmpGames(h, Game.Integer(0)) == 0) # False
