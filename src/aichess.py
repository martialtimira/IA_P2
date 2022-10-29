#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:22:03 2022

@author: ignasi
"""

import chess
import numpy as np
import sys
import queue
from typing import List

RawStateType = List[List[List[int]]]

from itertools import permutations


class Aichess():
    """
    A class to represent the game of chess.

    ...

    Attributes:
    -----------
    chess : Chess
        represents the chess game

    Methods:
    --------
    startGame(pos:stup) -> None
        Promotes a pawn that has reached the other side to another, or the same, piece

    """

    def __init__(self, TA, myinit=True):

        if myinit:
            self.chess = chess.Chess(TA, True)
        else:
            self.chess = chess.Chess([], False)

        self.listNextStatesW = []
        self.listNextStatesB = []
        self.listVisitedStates = []
        self.pathToTarget = []
        self.currentStateW = self.chess.boardSim.currentStateW;
        self.currentStateB = self.chess.boardSim.currentStateB;
        self.depthMax = 8;
        self.checkMate = False

    def getCurrentStateW(self):

        return self.currentStateW

    def getCurrentStateB(self):
        return self.currentStateB
    def getListNextStatesW(self, myState):

        self.chess.boardSim.getListNextStatesW(myState)
        self.listNextStatesW = self.chess.boardSim.listNextStatesW.copy()

        return self.listNextStatesW
    def getListNextStatesB(self, myState):

        self.chess.boardSim.getListNextStatesB(myState)
        self.listNextStatesB = self.chess.boardSim.listNextStatesB.copy()

        return self.listNextStatesB

    def isSameState(self, a, b):

        isSameState1 = True
        # a and b are lists
        for k in range(len(a)):

            if a[k] not in b:
                isSameState1 = False

        isSameState2 = True
        # a and b are lists
        for k in range(len(b)):

            if b[k] not in a:
                isSameState2 = False

        isSameState = isSameState1 and isSameState2
        return isSameState

    def isVisited(self, mystate):

        if (len(self.listVisitedStates) > 0):
            perm_state = list(permutations(mystate))

            isVisited = False
            for j in range(len(perm_state)):

                for k in range(len(self.listVisitedStates)):

                    if self.isSameState(list(perm_state[j]), self.listVisitedStates[k]):
                        isVisited = True

            return isVisited
        else:
            return False

    def getMoveFromStates(self, currentState, nextState):
        """
        Returns the "start" and "to" points of a move from its 2 states
        Args:
            currentState: Current State of the board
            nextState: State of the Board after the move
        Returns: Starting coordinates, To coordinates, piece ID
        """
        start = None
        to = None
        piece = None

        for element in currentState:  # compare each element of both states, to find the one in the current state that isn't
            if element not in nextState:  # on the next state, and define that one as the starting point, also define which piece it is
                start = (element[0], element[1])
                piece = element[2]
        for element in nextState:  # repeat, but instead find the one in nextState that isn't in currentState, and
            if element not in currentState:  # define that one as the "to" point.
                to = (element[0], element[1])

        return start, to, piece

    def isCheckMateW(self, mystate):

        # Your Code
        currentStateW = mystate
        currentStateB = self.getCurrentStateB()
        b_king = None
        b_tower = None
        w_king = None
        w_tower = None
        threatened = False
        for piece in currentStateW:
            if piece[2] == 2:
                w_tower = piece.copy()
            if piece[2] == 6:
                w_king = piece.copy()

        for piece in currentStateB:
            if piece[2] == 12:
                b_king = piece.copy()
            if piece[2] ==8:
                b_tower = piece.copy()
        black_king = self.chess.boardSim.board[b_king[0]][b_king[1]]
        if black_king.is_valid_move(self.chess.boardSim, (b_king[0], b_king[1]), (w_king[0], w_king[1]), False):
            return False

        for piece in currentStateW:                                         #Check if any piece of the current state Threatens the Black King
            currentPiece = self.chess.boardSim.board[piece[0]][piece[1]]
            if currentPiece != None:
                if(currentPiece.is_valid_move(self.chess.boardSim, (piece[0], piece[1]), (b_king[0], b_king[1])), False):
                    threatened = True

        if threatened:
            nextStatesB = self.getListNextStatesB(currentStateB)
            for state in nextStatesB:                                       #Check if Black King can escape to a "non threatened" position or Black Tower can take the White one to avoid CheckMate
                for piece in state:
                    if piece[2] == 12 and piece != b_king:                  #Check if Black king can escape
                        is_safe = True
                        for whitePiece in currentStateW:
                            attackerPiece = self.chess.boardSim.board[whitePiece[0]][whitePiece[1]]
                            self.chess.moveSim((b_king[0], b_king[1]), (piece[0], piece[1]), False)
                            if attackerPiece != None:
                                if attackerPiece.is_valid_move(self.chess.boardSim, (whitePiece[0], whitePiece[1]), (piece[0], piece[1]), False):
                                    is_safe = False
                            self.chess.moveSim((piece[0], piece[1]), (b_king[0], b_king[1]), False)
                        if is_safe:
                            return False
                        black_king = self.chess.boardSim.board[b_king[0]][b_king[1]]
                        if black_king.is_valid_move(self.chess.boardSim, (b_king[0], b_king[1]), (w_tower[0], w_tower[1]), False): #Check if Tower is close enough to the King that it can take it to avoid CheckMate
                            return False

                    if piece[2] == 8 and piece != b_tower and piece[0] == w_tower[0] and piece[1] == w_tower[1]:            #Check if Black Tower can take the White one to avoid CheckMate
                        blackTower = self.chess.boardSim.board[b_tower[0]][b_tower[1]]
                        if blackTower.is_valid_move(self.chess.boardSim, (b_tower[0], b_tower[1]), (w_tower[0], w_tower[1]), False):
                            return False

        else:
            return False

        self.checkMate = True
        return True

    def isCheckMateB(self, mystate):
        # Your Code
        currentStateB = mystate
        currentStateW = self.getCurrentStateW()
        b_king = None
        b_tower = None
        w_king = None
        w_tower = None
        threatened = False
        for piece in currentStateB:
            if piece[2] == 8:
                b_tower = piece.copy()
            if piece[2] == 12:
                b_king = piece.copy()

        for piece in currentStateW:
            if piece[2] == 6:
                w_king = piece.copy()
            if piece[2] == 2:
                w_tower = piece.copy()
        white_king = self.chess.boardSim.board[w_king[0]][w_king[1]]
        if white_king.is_valid_move(self.chess.boardSim, (w_king[0], w_king[1]), (b_king[0], b_king[1]), False):
            return False

        for piece in currentStateB:                                         #Check if any piece of the current state Threatens the White King
            currentPiece = self.chess.boardSim.board[piece[0]][piece[1]]
            if currentPiece != None:
                if(currentPiece.is_valid_move(self.chess.boardSim, (piece[0], piece[1]), (w_king[0], w_king[1]), False)):
                    threatened = True

        if threatened:
            nextStatesW = self.getListNextStatesW(currentStateW)
            for state in nextStatesW:                                       #Check if White King can escape to a "non threatened" position or White Tower can take the Black one to avoid CheckMate
                for piece in state:
                    if piece[2] == 6 and piece != w_king:                  #Check if White king can escape
                        is_safe = True
                        for blackPiece in currentStateB:
                            attackerPiece = self.chess.boardSim.board[blackPiece[0]][blackPiece[1]]
                            self.chess.moveSim((w_king[0], w_king[1]), (piece[0], piece[1]), False)
                            if attackerPiece != None:
                                if attackerPiece.is_valid_move(self.chess.boardSim, (blackPiece[0], blackPiece[1]), (piece[0], piece[1]), False):
                                    is_safe = False
                            self.chess.moveSim((piece[0], piece[1]), (w_king[0], w_king[1]), False)
                        if is_safe:
                            return False
                        white_king = self.chess.boardSim.board[w_king[0]][w_king[1]]
                        if white_king.is_valid_move(self.chess.boardSim, (w_king[0], w_king[1]), (b_tower[0], b_tower[1]), False): #Check if Tower is close enough to the King that it can take it to avoid CheckMate
                            return False
                    if piece[2] == 2 and piece != w_tower and piece[0] == b_tower[0] and piece[1] == b_tower[1]:            #Check if White Tower can take the Black one to avoid CheckMate
                        whiteTower = self.chess.boardSim.board[w_tower[0]][w_tower[1]]
                        if whiteTower.is_valid_move(self.chess.boardSim, (piece[0], piece[1]), (b_tower[0], b_tower[1]), False):
                            return False

        else:
            return False

        self.checkMate = True
        return True

    def utility(self, state):
        utility = 15.06225774829855           #start with a neutral utility score
        w_king = None
        b_king = None
        w_tower = None

        if self.isCheckMateW(state):            #if it's check mate, return the utility score
            return utility
        if self.isCheckMateB(self.getCurrentStateB()):
            return -utility

        for piece in state:
            if piece[2] == 6:
                w_king = piece.copy()
            if piece[2] == 2:
                w_tower = piece.copy()
        for piece in self.getCurrentStateB():
            if piece[2] == 12:
                b_king = piece.copy()

        w_king_array = np.array([w_king[0], w_king[1]])         #make arrays of positions of white king
        b_king_array = np.array([b_king[0], b_king[1]])         #black king
        w_tower_array = np.array([w_tower[0], w_tower[1]])      #white tower

        if w_tower != None:                                     #if White tower isn't taken, check if it's in the same
            if w_tower[0] != b_king[0] and w_tower[1] != b_king[1]: #row or column as the black king, and if it isn't
                utility -= np.linalg.norm(w_tower_array - b_king_array) #subtract its euclidean distance to the utility score

        if (b_king[0] != 0 and b_king[0] != 7) and (b_king[1] != 0 and b_king[1] != 7): #If the black king isn't on an edge of the board
            if b_king[0] != 0 and b_king[0] != 7:                                       #Subtract the minimum between the 2 axis distances to the nearest edge
                utility -= min(b_king[0], (7 - b_king[0])) * 2
            if b_king[1] != 0 and b_king[1] != 7:
                utility -= min(b_king[1], (7 - b_king[1])) * 2

        utility -= np.linalg.norm(w_king_array - b_king_array)      #subtract the euclidean distance between the 2 kings
        return utility

    #TRY TWEAKING MAX AND MINVALUES TO RETURN THE PATH (state_list and whatever)
    def miniMax(self, mystate, depth):
        self.depthMax = depth
        move = ()
        if self.isCheckMateW(mystate):
            return move

        v, state_list = self.max_value(mystate, 0)
        print("CS: ", mystate)
        print("SL: ", state_list)
        print("V: ", v)
        for state in self.getListNextStatesW(mystate):
            start, to, piece = self.getMoveFromStates(mystate, state)
            self.chess.moveSim(start, to, False)
            if self.utility(state) == v:
                print("found")
                print(mystate)
                print(state)
                print(v)
                start_f, to_f, piece_f = self.getMoveFromStates(mystate, state)
                move = (start_f, to_f)
                self.chess.moveSim(to, start, False)
                return move
            self.chess.moveSim(to, start, False)
        return move

    def max_value(self, mystate, depth):
        if depth > self.depthMax or self.isCheckMateW(mystate):
            return self.utility(mystate), mystate
        v = -sys.maxsize
        for state in self.getListNextStatesW(mystate):
            start, to, piece = self.getMoveFromStates(mystate, state)
            self.chess.moveSim(start, to, False)
            t, state_list = self.min_value(state, depth+1)
            v = max(v, t)
            self.chess.moveSim(to, start, False)
        return v, state_list

    def min_value(self, mystate, depth):

        currentState = self.getCurrentStateB().copy()
        if depth > self.depthMax or self.isCheckMateW(mystate):
            return self.utility(mystate), mystate
        v = sys.maxsize

        for state in self.getListNextStatesB(currentState):
            start, to, piece = self.getMoveFromStates(currentState, state)
            self.chess.moveSim(start, to, False)
            t, state_list = self.max_value(self.getCurrentStateW(), depth + 1)
            v = min(v, t)
            self.chess.moveSim(to, start, False)
        return v, state_list

def translate(s):
    """
    Translates traditional board coordinates of chess into list indices
    """

    try:
        row = int(s[0])
        col = s[1]
        if row < 1 or row > 8:
            print(s[0] + "is not in the range from 1 - 8")
            return None
        if col < 'a' or col > 'h':
            print(s[1] + "is not in the range from a - h")
            return None
        dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        return (8 - row, dict[col])
    except:
        print(s + "is not in the format '[number][letter]'")
        return None


if __name__ == "__main__":
    #   if len(sys.argv) < 2:
    #       sys.exit(usage())

    # intiialize board
    TA = np.zeros((8, 8))
    # white pieces
    # TA[0][0] = 2
    # TA[2][4] = 6
    # # black pieces
    # TA[0][4] = 12

    #White pieces
    TA[7][0] = 2
    TA[7][4] = 6
    #TA[0][0] = 2
    #TA[2][4] = 6
    #Black pieces
    TA[0][7] = 8
    TA[0][4] = 12

    # initialise board
    print("stating AI chess... ")
    aichess = Aichess(TA, True)
    currentStateW = aichess.chess.board.currentStateW.copy()
    currentStateB = aichess.chess.board.currentStateB.copy()
    print("printing board")
    aichess.chess.boardSim.print_board()

    # get list of next states for current state
    print("current State Whites", currentStateW)
    print("current State Blacks", currentStateB)

    # it uses board to get them... careful 
    aichess.getListNextStatesW(currentStateW)
    aichess.getListNextStatesB(currentStateB)
    #   aichess.getListNextStatesW([[7,4,2],[7,4,6]])

    print("list next White states(,", len(aichess.listNextStatesW), "): ", aichess.listNextStatesW)
    print("list next Black states(,", len(aichess.listNextStatesB), "): ", aichess.listNextStatesB)

    # starting from current state find the end state (check mate) - recursive function
    # aichess.chess.boardSim.listVisitedStates = []
    # find the shortest path, initial depth 0
    depth = 1

    print("Next move: ", aichess.miniMax(currentStateW, depth))
    #print("U: ", aichess.utility(currentStateW))
    #print(aichess.getCurrentStateB())
    #aichess.chess.moveSim((0,7), (1,7))
    #print(aichess.getCurrentStateB())

    aichess.chess.boardSim.print_board()
    print("#Move sequence...  ", aichess.pathToTarget)
    print("#Visited sequence...  ", aichess.listVisitedStates)
    print("#Current State...  ", aichess.chess.board.currentStateW)
    #print("#Checkmate Status White: ", aichess.isCheckMateW(currentStateW))
    #print("#Checkmate Status Black: ", aichess.isCheckMateB(currentStateB))
