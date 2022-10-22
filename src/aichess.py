#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:22:03 2022

@author: ignasi
"""
import copy

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
                w_tower = piece

        for piece in currentStateB:
            if piece[2] == 12:
                b_king = piece
            if piece[2] == 8:
                b_tower = piece

        for piece in currentStateW:  # Check if any piece of the current state Threatens the Black King
            currentPiece = self.chess.boardSim.board[piece[0]][piece[1]]
            if currentPiece.is_valid_move(self.chess.boardSim, (piece[0], piece[1]), (b_king[0], b_king[1])):
                threatened = True

        if threatened:
            nextStatesB = self.getListNextStatesB(currentStateB)
            for state in nextStatesB:  # Check if Black King can escape to a "non threatened" position or Black Tower can take the White one to avoid CheckMate
                for piece in state:
                    if piece[2] == 12 and piece != b_king:  # Check if Black king can escape
                        is_safe = True
                        for whitePiece in currentStateW:
                            attackerPiece = self.chess.boardSim.board[whitePiece[0]][whitePiece[1]]
                            self.chess.moveSim((b_king[0], b_king[1]), (piece[0], piece[1]), False)
                            if attackerPiece.is_valid_move(self.chess.boardSim, (whitePiece[0], whitePiece[1]), (piece[0], piece[1])):
                                is_safe = False
                            self.chess.moveSim((piece[0], piece[1]), (b_king[0], b_king[1]), False)
                        if is_safe:
                            return False
                        black_king = self.chess.boardSim.board[b_king[0]][b_king[1]]
                        if black_king.is_valid_move(self.chess.boardSim, (b_king[0], b_king[1]), (w_tower[0], w_tower[1])): #Check if Tower is close enough to the King that it can take it to avoid CheckMate
                            return False

                    if piece[2] == 8 and piece != b_tower and piece[0] == w_tower[0] and piece[1] == w_tower[1]:            #Check if Black Tower can take the White one to avoid CheckMate
                        blackTower = self.chess.boardSim.board[b_tower[0]][b_tower[1]]
                        self.chess.moveSim((b_tower[0], b_tower[1]), (piece[0], piece[1]), False)
                        if blackTower.is_valid_move(self.chess.boardSim, (piece[0], piece[1]), (w_tower[0], w_tower[1])):
                            return False
                        self.chess.moveSim((piece[0], piece[1]), (b_tower[0], b_tower[1]), False)

        else:
            return False

            # print(currentPiece.is_valid_move(self.chess.boardSim, (piece[0], piece[1]), (0, 2)))
        self.checkMate = True
        return True

    def evaluaEstat(self):
        return 0

    def min(self, depth):

        if depth is not 0:
            depth -= 1
            minim = sys.maxint
            now = self.getCurrentStateB()
            future_state = None
            path = None

            for estat in self.getListNextStatesB(now):
                start, to, piece = self.getMoveFromStates(now, estat)
                self.chess.moveSim(start, to)
                t, e = self.max(depth)
                if minim > t:
                    minim = t
                    future_state = estat
                    path = e
                start, to, piece = self.getMoveFromStates(estat, now)
                self.chess.moveSim(start, to)

            path.append(future_state)
            return minim, path

        return self.evaluaEstat(), []

    # S'inicia minimax cridant a max primer
    def max(self, depth):

        if depth is not 0:
            depth -= 1
            maxim = - sys.maxint
            now = self.getCurrentStateW()
            future_state = None
            path = None

            for estat in self.getListNextStatesW(now):
                start, to, piece = self.getMoveFromStates(now, estat)
                self.chess.moveSim(start, to)
                t, e = self.min(now)
                if maxim < t:
                    maxim = t
                    future_state = estat
                    path = e
                start, to, piece = self.getMoveFromStates(estat, now)
                self.chess.moveSim(start, to)

            path.append(future_state)
            return maxim, path

        return self.evaluaEstat(), []


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
    TA[0][0] = 2
    TA[2][4] = 6
    # # black pieces
    TA[0][6] = 8
    TA[0][4] = 12

    # White pieces
    # TA[0][3] = 2
    # TA[2][4] = 6
    # Black pieces
    # TA[2][0] = 8
    # TA[0][4] = 12

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
    depth = 0

    aichess.chess.boardSim.print_board()
    print("#Move sequence...  ", aichess.pathToTarget)
    print("#Visited sequence...  ", aichess.listVisitedStates)
    print("#Current State...  ", aichess.chess.board.currentStateW)
    print("#Checkmate Status: ", aichess.isCheckMateW(currentStateW))
