# Combinatorial_Games
Implementation of CGSuite's language CGScript<sup>1</sup> in Python.

# Quick Introduction

# List of Files

- `rep.py`: Implements the *read-eval-print* loop for the command-line interface
- `games.py`: Defines the `Game` class and associated methods

# Detailed Overview

The limited subset of CGScript to be implemented consists of three types of statements:
- Expressions: 
    - Game: `{ expression [, expression]* | expression [, expression]* }`
    - Arithmetic: `[-]* expression [op expression]*` where `op` can be `+` or `-`. (More, such as Cooling and Heating, will be implemented later, eventually.)
    - Name: common games, numbers, nimbers, up-multiples, or user-defined names.
- Assignment statements: `name := expression`
- Comparison statements: `expression <= expression`

## Read-Eval-Print Loop

Follows these steps:
1. Print prompt (probably just `>`).
2. Accepts user input up to end of line.
3. Parses user input into a series of Python commands
4. Runs Python commands
5. Prints out result

## Game Class

The `Game` class has a list of Left options and a list of Right options. It also has a name, which is hashed to produce a unique identifier. Common games have certain predefined names, while other games will have a generated name. The hash values are equal for equivalent games. This means that `{|}` and `{-1|1}` will have the same hash value.
A Game can be constructed via several different methods. There are methods to construct certain common games, such as integers, dyadic rationals, nimbers, and up-multiples (maybe?). Also a method to construct a Game from the lists of its Left and Right options, which reduces it to canonical form by removing dominated and reversible options before generating a name for the Game.
There is a method to compare two Games, which is recursive, and so uses the hash values to store previously computed comparisons. There are four possibilities when comparing games, equal to, less than, greater than, fuzzy with.


<sup>1</sup> CGSuite was designed and developed by Aaron Siegel (asiegel@users.sourceforge.net), for more information, visit [CGSuite](https://www.cgsuite.org).
