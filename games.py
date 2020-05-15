#!/usr/bin/python3

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
    def __init__(self, LeftOptions, RightOptions):
        self.LeftOptions = LeftOptions
        self.RightOptions = RightOptions
        # check for dominated options
        # check for reversible options
        # generate name

    def __hash__(self):
        return hash(self.name)
