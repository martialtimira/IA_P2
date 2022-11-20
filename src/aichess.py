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
import piece
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
        if w_tower == None or w_king == None:
            return False
        for piece in currentStateB:
            if piece[2] == 12:
                b_king = piece.copy()
            if piece[2] ==8:
                b_tower = piece.copy()
        black_king = self.chess.boardSim.board[b_king[0]][b_king[1]]
        if black_king != None:
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

                    if b_tower != None and w_tower != None:
                        if piece[2] == 8 and piece != b_tower and piece[0] == w_tower[0] and piece[1] == w_tower[
                            1]:  # Check if Black Tower can take the White one to avoid CheckMate
                            blackTower = self.chess.boardSim.board[b_tower[0]][b_tower[1]]
                            if blackTower.is_valid_move(self.chess.boardSim, (b_tower[0], b_tower[1]),
                                                        (w_tower[0], w_tower[1]), False):
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

        if b_tower == None or b_king == None:
            return False

        for piece in currentStateW:
            if piece[2] == 6:
                w_king = piece.copy()
            if piece[2] == 2:
                w_tower = piece.copy()
        if w_king == None:
            return True
        white_king = None
        if w_king != None:
            white_king = self.chess.boardSim.board[w_king[0]][w_king[1]]
        if white_king != None:
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

    def utilityW(self, state):
        utility = 0
        white_score = 0
        black_score = 0
        for piece in state:
            if piece[2] == 6:
                white_score += 500
            if piece[2] == 2:
                white_score += 100
        for piece in self.chess.boardSim.currentStateB:
            if piece[2] == 12:
                black_score += 500
            if piece[2] == 8:
                black_score += 100

        if self.isCheckMateW(state):
            white_score += 1000
        if self.isCheckMateB(self.chess.boardSim.currentStateB):
            black_score += 1000

        utility = white_score - black_score
        return utility

    #MiniMax, max_value and min_value for white pieces
    def miniMaxW(self, mystate, depth):
        self.depthMax = depth
        move = ()
        if self.isCheckMateW(mystate):
            return move

        v, state_list = self.max_valueW(mystate, 0)
        if len(state_list) == 2:
            print("SL: ", state_list)
            start, to, piece = self.getMoveFromStates(self.currentStateW, state_list)
            move = (start, to)

        return move

    def max_valueW(self, mystate, depth):
        return_state = mystate
        initial_list = [mystate]
        if depth > self.depthMax or self.isCheckMateW(mystate):
            return self.utilityW(mystate), return_state
        v = -sys.maxsize
        nextStateList = self.getListNextStatesW(mystate)
        for state in nextStateList:
            start, to, piece_moved = self.getMoveFromStates(mystate, state)
            pieceThere = self.chess.boardSim.board[to[0]][to[1]]
            pieceToMove = self.chess.boardSim.board[start[0]][start[1]]
            if pieceToMove != None:
                if pieceToMove.is_valid_move(self.chess.boardSim, start, to):
                    self.chess.moveSim(start, to, False)
                    t, state_list = self.min_valueW(state, depth + 1)
                    #v = max(v, t)
                    if t > v:
                        v = t
                        return_state = state

                    self.chess.moveSim(to, start, False)
                    if pieceThere != None:
                        if pieceThere.name == 'R' and not pieceThere.color:
                            self.chess.boardSim.board[to[0]][to[1]] = piece.Rook(False)
                        if pieceThere.name == 'K' and not pieceThere.color:
                            self.chess.boardSim.board[to[0]][to[1]] = piece.King(False)
                        if pieceThere.name == 'R' and pieceThere.color:
                            self.chess.boardSim.board[to[0]][to[1]] = piece.Rook(True)
                        if pieceThere.name == 'K' and pieceThere.color:
                            self.chess.boardSim.board[to[0]][to[1]] = piece.King(True)
                    self.refresh_states()

        return v, return_state

    def min_valueW(self, mystate, depth):
        return_state = mystate
        initial_list = [mystate]
        currentState = self.getCurrentStateB().copy()
        if depth > self.depthMax or self.isCheckMateW(mystate):
            return self.utilityW(mystate), return_state
        v = sys.maxsize

        for state in self.getListNextStatesB(currentState):
            start, to, piece_moved = self.getMoveFromStates(currentState, state)
            pieceThere = self.chess.boardSim.board[to[0]][to[1]]
            pieceToMove = self.chess.boardSim.board[start[0]][start[1]]
            if pieceToMove != None:
                if pieceToMove.is_valid_move(self.chess.boardSim, start, to):
                    self.chess.moveSim(start, to, False)
                    t, state_list = self.max_valueW(self.getCurrentStateW(), depth + 1)
                    v = min(v, t)
                    if t < v:
                        v = t
                        return_state = state
                    self.chess.moveSim(to, start, False)
                    if pieceThere != None:
                        if pieceThere.name == 'R' and not pieceThere.color:
                            self.chess.boardSim.board[to[0]][to[1]] = piece.Rook(False)
                        if pieceThere.name == 'K' and not pieceThere.color:
                            self.chess.boardSim.board[to[0]][to[1]] = piece.King(False)
                        if pieceThere.name == 'R' and pieceThere.color:
                            self.chess.boardSim.board[to[0]][to[1]] = piece.Rook(True)
                        if pieceThere.name == 'K' and pieceThere.color:
                            self.chess.boardSim.board[to[0]][to[1]] = piece.King(True)
                    self.refresh_states()
        return v, return_state

    #Utility Mini-Max, Min-Value and Max-Value for black pieces

    def utilityB(self, state):
        utility = 15.06225774829855           #start with a neutral utility score
        b_king = None
        w_king = None
        b_tower = None
        w_tower = None

        if self.isCheckMateB(state):            #if it's check mate, return the utility score
            return utility
        if self.isCheckMateW(self.getCurrentStateW()):
            return -utility

        for piece in state:
            if piece[2] == 12:
                w_king = piece.copy()
            if piece[2] == 8:
                b_tower = piece.copy()
        for piece in self.getCurrentStateW():
            if piece[2] == 6:
                b_king = piece.copy()
            if piece[2] == 2:
                w_tower = piece.copy()
        w_king_array = np.array([w_king[0], w_king[1]])         #make arrays of positions of black king
        b_king_array = np.array([b_king[0], b_king[1]])         #white king
        if b_tower != None:
            b_tower_array = np.array([b_tower[0], b_tower[1]])      #white tower

        #maybe change this
        white_tower = self.chess.boardSim.board[w_tower[0]][w_tower[1]]

        white_king = self.chess.boardSim.board[w_king[0]][w_king[1]]

        if white_king != None and b_tower != None:
            if (white_king.is_valid_move(self.chess.boardSim, (w_king[0], w_king[1]), (b_tower[0], b_tower[1])) or
                white_king.is_valid_move(self.chess.boardSim, (w_king[0], w_king[1]), (b_king[0], b_king[1]))):
                utility -= 10

        if white_tower != None:
            if white_tower.is_valid_move(self.chess.boardSim, (w_tower[0], w_tower[1]), (b_king[0], b_king[1])):
                utility -= 10
        #until here

        if b_tower != None:                                     #if black tower isn't taken, check if it's in the same
            if b_tower[0] != w_king[0] and b_tower[1] != w_king[1]: #row or column as the white king, and if it isn't
                utility -= np.linalg.norm(b_tower_array - w_king_array) / 10 #subtract its euclidean distance to the utility score
            #if b_tower[0] == w_king[0] or w_tower[1] == w_king[1]:
                #utility += np.linalg.norm(b_tower_array - w_king_array) / 5

        if (w_king[0] != 0 and w_king[0] != 7) and (w_king[1] != 0 and w_king[1] != 7): #If the white king isn't on an edge of the board
            if w_king[0] != 0 and w_king[0] != 7:                                       #Subtract the minimum between the 2 axis distances to the nearest edge
                utility -= min(w_king[0], (7 - w_king[0])) * 4
            if w_king[1] != 0 and w_king[1] != 7:
                utility -= min(w_king[1], (7 - w_king[1])) * 4

        dist = np.linalg.norm(b_king_array - w_king_array)

        if dist == 1.0:
            utility -= 10
        else:
            utility -= dist * 10    #subtract the euclidean distance between the 2 kings
        return utility

    #FIX TO MATCH THE WHITE VERSION UPDATES
    def miniMaxB(self, mystate, depth):
        self.depthMax = depth
        move = ()
        if self.isCheckMateB(mystate):
            return move

        v, state_list = self.max_valueB(mystate, 0)
        if len(state_list) == 2:
            start, to, piece = self.getMoveFromStates(self.currentStateB, state_list[1])
            move = (start, to)

        return move

    # FIX TO MATCH THE WHITE VERSION UPDATES
    def max_valueB(self, mystate, depth):
        return_state = [mystate]
        initial_list = [mystate]
        if depth > self.depthMax or self.isCheckMateB(mystate):
            return self.utilityB(mystate), return_state
        v = -sys.maxsize
        for state in self.getListNextStatesB(mystate):
            start, to, piece_moved = self.getMoveFromStates(mystate, state)
            pieceThere = self.chess.boardSim.board[to[0]][to[1]]
            self.chess.moveSim(start, to, False)
            t, state_list = self.min_valueB(state, depth + 1)
            #v = max(v, t)
            if t > v:
                v = t
                return_state = initial_list + state_list

            self.chess.moveSim(to, start, False)
            if pieceThere != None:
                if pieceThere.name == 'R' and not pieceThere.color:
                    self.chess.boardSim.board[to[0]][to[1]] = piece.Rook(False)
                if pieceThere.name == 'K' and not pieceThere.color:
                    self.chess.boardSim.board[to[0]][to[1]] = piece.King(False)
                if pieceThere.name == 'R' and pieceThere.color:
                    self.chess.boardSim.board[to[0]][to[1]] = piece.Rook(True)
                if pieceThere.name == 'K' and pieceThere.color:
                    self.chess.boardSim.board[to[0]][to[1]] = piece.King(True)
            self.refresh_states()

        return v, return_state

    # FIX TO MATCH THE WHITE VERSION UPDATES
    def min_valueB(self, mystate, depth):
        return_state = [mystate]
        initial_list = [mystate]
        currentState = self.getCurrentStateW().copy()

        if depth > self.depthMax or self.isCheckMateB(mystate):
            return self.utilityB(mystate), return_state
        v = sys.maxsize

        for state in self.getListNextStatesW(currentState):
            start, to, piece_moved = self.getMoveFromStates(currentState, state)
            pieceThere = self.chess.boardSim.board[to[0]][to[1]]
            self.chess.moveSim(start, to, False)
            t, state_list = self.max_valueB(self.getCurrentStateB(), depth + 1)
            v = min(v, t)
            if t < v:
                v = t
                return_state = initial_list + state_list
            self.chess.moveSim(to, start, False)
            if pieceThere != None:
                if pieceThere.name == 'R' and not pieceThere.color:
                    self.chess.boardSim.board[to[0]][to[1]] = piece.Rook(False)
                if pieceThere.name == 'K' and not pieceThere.color:
                    self.chess.boardSim.board[to[0]][to[1]] = piece.King(False)
                if pieceThere.name == 'R' and pieceThere.color:
                    self.chess.boardSim.board[to[0]][to[1]] = piece.Rook(True)
                if pieceThere.name == 'K' and pieceThere.color:
                    self.chess.boardSim.board[to[0]][to[1]] = piece.King(True)
            self.refresh_states()
        return v, return_state

    def refresh_states(self):
        self.chess.boardSim.currentStateB.clear()
        self.chess.boardSim.currentStateW.clear()

        for row in range(len(self.chess.boardSim.board)):
            for column in range(len(self.chess.boardSim.board[row])):
                if self.chess.boardSim.board[row][column] != None:
                    piece = self.chess.boardSim.board[row][column]
                    if piece.color:
                        if piece.name == 'K':
                            self.chess.boardSim.currentStateW.append([row, column, 6])
                        if piece.name == 'R':
                            self.chess.boardSim.currentStateW.append([row, column, 2])
                    else:
                        if piece.name == 'K':
                            self.chess.boardSim.currentStateB.append([row, column, 12])
                        if piece.name == 'R':
                            self.chess.boardSim.currentStateB.append([row, column, 8])

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
    depth = 3
    move_number = 0

    print("UTILITYW: ", aichess.utilityW(currentStateW))
    print(aichess.getListNextStatesW(currentStateW))
    while not aichess.isCheckMateW(aichess.getCurrentStateW()):
        currentStateW = aichess.getCurrentStateW()
        print("NEXT STATES: ", aichess.getListNextStatesW(currentStateW))
        nextMove = aichess.miniMaxW(currentStateW, depth)
        print("NM: ", nextMove)
        aichess.chess.moveSim(nextMove[0],nextMove[1], True)
        aichess.chess.boardSim.print_board()
        move_number += 1

    #while not (aichess.isCheckMateB(aichess.getCurrentStateB()) or aichess.isCheckMateW(aichess.getCurrentStateW())):
        #nextMove = aichess.miniMaxW(aichess.getCurrentStateW(), depth)
        #print("W move: ", nextMove)
        #aichess.chess.moveSim(nextMove[0], nextMove[1])
        #aichess.chess.boardSim.print_board()
        #print("WHITESTATE: ", aichess.getCurrentStateW())
        #print("BLACKSTATE: ", aichess.getCurrentStateB())
        #move_number += 1
        #nextMove = aichess.miniMaxB(aichess.getCurrentStateB(), depth)
        #print("B Move: ", nextMove)
        #aichess.chess.moveSim(nextMove[0],nextMove[1])
        #aichess.chess.boardSim.print_board()
        #print("WHITESTATE: ", aichess.getCurrentStateW())
        #print("BLACKSTATE: ", aichess.getCurrentStateB())
        #move_number += 1

    #aichess.chess.moveSim((7,7), (0,7))
    print("WHITESTATE: ", aichess.getCurrentStateW())
    print("BLACKSTATE: ", aichess.getCurrentStateB())

    aichess.chess.boardSim.print_board()
    print("#Moves Performed: ", move_number)
    print("#Move sequence...  ", aichess.pathToTarget)
    print("#Visited sequence...  ", aichess.listVisitedStates)
    print("#Current State...  ", aichess.chess.board.currentStateW)
    print("#Checkmate Status White: ", aichess.isCheckMateW(aichess.getCurrentStateW()))
    print("#Checkmate Status Black: ", aichess.isCheckMateB(aichess.getCurrentStateB()))
