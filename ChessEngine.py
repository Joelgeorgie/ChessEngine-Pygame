
class GameState():

    def __init__(self):
        """
        Initialises the board as a 2D array with respective pieces. 
        """
        self.board=[
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bP','bP','bP','bP','bP','bP','bP','bP'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wP','wP','wP','wP','wP','wP','wP','wP'],
             ['wR','wN','wB','wQ','wK','wB','wN','wR']
        ]
        self.moveFunctions={
            'P' : self.getPawnMoves,'R' : self.getRookMoves , 'N' : self.getKnightMoves , "B" : self.getBishopMoves ,
            "K" : self.getKingMoves, "Q" : self.getQueenMoves 
        }
        self.whiteToMove=True
        self.movelog=[]
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible=()
        self.currentCastlingRights = CastleRights(True,True,True,True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,self.currentCastlingRights.wqs,self.currentCastlingRights.bqs)]

    def makeMove(self,move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = '--'
        self.movelog.append(move)
        self.whiteToMove = not self.whiteToMove
        
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow,move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #en-passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'
            

        #enpassant update
        if move.pieceMoved[1] == 'P' and abs(move.startRow-move.endRow) == 2 :      #only on 2 square advance
            self.enPassantPossible = ((move.startRow+move.endRow)//2,move.endCol)
            
        else:
            self.enPassantPossible = ()
        
        #castling move
        if move.isCastleMove:
            if move.endCol-move.startCol == 2:
                self.board[move.startRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.startRow][move.endCol+1] = '--'
            else:
                self.board[move.startRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.startRow][move.endCol-2] = '--'

        #update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,self.currentCastlingRights.wqs,self.currentCastlingRights.bqs))


    def undoMove(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow,move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow,move.startCol)
            #undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow,move.endCol)

            else:
                self.enPassantPossible = ()

            #undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRights = self.castleRightsLog[-1]

            #undo castlemove
            if move.isCastleMove:
                if move.endCol-move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.startRow][move.endCol-1] 
                    self.board[move.startRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.startRow][move.endCol+1] 
                    self.board[move.startRow][move.endCol+1] = '--'
    

    def updateCastleRights(self,move):
        if move.pieceMoved == 'wK' :
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK' :
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False

        elif move.pieceMoved == 'wR' and move.startRow == 7:
            if move.startCol == 0:
                self.currentCastlingRights.wqs = False
            elif move.startCol == 7:
                self.currentCastlingRights.wks = False

        elif move.pieceMoved == 'bR' and move.startRow == 0:
            if move.startCol == 0:
                self.currentCastlingRights.bqs = False
            elif move.startCol == 7:
                self.currentCastlingRights.bks = False

    # All moves  considering checks
    def getValidMoves(self):
        tempEnpassantPossible = self.enPassantPossible
        tempCastleRights = self.currentCastlingRights
        moves =  self.getAllPossibleMoves()

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0] , self.whiteKingLocation[1] , moves )
        
        else:
            self.getCastleMoves(self.blackKingLocation[0] , self.blackKingLocation[1] , moves )

        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        self.enPassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1]) 
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])  

    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False



    # All possible Moves  without considering checks  
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]

                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece=self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves


    # Get all the pawn moves
    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--":                          #To move 1 square in front if its free
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--":           #To move 2 square in front if its free  from intital
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c >= 1 :
                if self.board[r-1][c-1][0] == "b" :                 #To capture black pieces 1 square diagonally left
                    moves.append(Move((r,c),(r-1,c-1),self.board)) 
                elif (r-1,c-1) == self.enPassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,isEnpassantMove=True))
            if c <= 6:
                if self.board[r-1][c+1][0] == "b" :                 #To capture black pieces 1 square diagonally right 
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1) == self.enPassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board,isEnpassantMove=True))
            
           
                                                           
        else:
            if self.board[r+1][c] == "--":                          #To move 1 square in front if its free
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--":           #To move 2 square in front if its free from intital
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c >= 1 :
                if self.board[r+1][c-1][0] == "w" :                 #To capture white pieces 1 square diagonally left
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1) == self.enPassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,isEnpassantMove=True)) 
            if c <= 6:
                if self.board[r+1][c+1][0] == "w" :                 #To capture white pieces 1 square diagonally right 
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1) == self.enPassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,isEnpassantMove=True))
            if r == 3:
                pass 

    # Get all the rook moves
    def getRookMoves(self,r,c,moves):
        direction = [(-1,0),(1,0),(0,1),(0,-1)]
        enemyC = 'b' if self.whiteToMove else "w"
        for d in direction:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0<=endRow<=7 and 0<=endCol<=7:
                    if self.board[endRow][endCol] == '--':
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif self.board[endRow][endCol][0] == enemyC:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else :
                        break

    # Get all the Knight moves
    def getKnightMoves(self,r,c,moves):
        knightMoves = [(2,-1),(2,1),(-2,1),(-2,-1),(1,-2),(1,2),(-1,-2),(-1,2)]
        allyC = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0<=endRow<=7 and 0<=endCol<=7:
                if self.board[endRow][endCol][0] != allyC:
                    moves.append(Move((r,c),(endRow,endCol),self.board))

    # Get all the Bishop moves
    def getBishopMoves(self,r,c,moves):
        direction = [(-1,-1),(-1,1),(1,-1),(1,1)]
        enemyC = 'b' if self.whiteToMove else "w"
        for d in direction:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0<=endRow<=7 and 0<=endCol<=7:
                    if self.board[endRow][endCol] == '--':
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif self.board[endRow][endCol][0] == enemyC:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else :
                        break

    # Get all the Queen moves
    def getQueenMoves(self,r,c,moves):
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)

    # Get all the King moves
    def getKingMoves(self,r,c,moves):
        kingMoves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        allyC = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0<=endRow<=7 and 0<=endCol<=7:
                if self.board[endRow][endCol][0] != allyC:
                    moves.append(Move((r,c),(endRow,endCol),self.board))
        
    
    #get all castle moves to be added to list of moves
    def getCastleMoves(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r,c,moves)

        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r,c,moves)

    def getKingSideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove = True))


    def getQueenSideCastleMoves(self,r,c,moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2) :
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove = True))

class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {
        "1" : 7 ,  "2" : 6 ,  "3" : 5 , "4" : 4 , "5" : 3 , "6" : 2 , "7" : 1 , "8" : 0
    }
    rowsToRanks = { v:k for k,v in ranksToRows.items()}
    filesToCols = {
        "a" : 0 ,  "b" : 1 ,  "c" : 2 , "d" : 3 , "e" : 4 , "f" : 5 , "g" : 6 , "h" : 7
    }
    colsToFiles = { v:k for k,v in filesToCols.items() }


    def __init__(self,startSq,endSq,board,isEnpassantMove=False , isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        #en-passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else  'bP'
        
        #castlemove
        self.isCastleMove = isCastleMove
        
        self.moveId = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

    def __eq__(self, other):
        if isinstance(other,Move):
            return self.moveId==other.moveId
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self , r , c):
        return self.colsToFiles[c] + self.rowsToRanks[r]