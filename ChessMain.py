
import pygame as p
import ChessEngine  

WIDTH=HEIGHT=400
DIMENSION=8
SQ_SIZE=HEIGHT//DIMENSION 
MAX_FPS=15
IMAGES={}

"""
        Load the images once to a dictionary so as to be accessed frequently
"""
def loadImages():
    pieces=['bK','bQ','bB','bN','bR','bP','wK','wQ','wB','wR','wN','wP']
    for piece in pieces:
        IMAGES[piece]=p.transform.scale(p.image.load('images/'+piece+'.png'),(SQ_SIZE,SQ_SIZE))







#Main driver
def main():
    p.init()
    screen=p.display.set_mode((HEIGHT,WIDTH))
    p.display.set_caption("Chess")
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    gs=ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False 


    loadImages()

    
    running = True
    sqSelected=()  #stores the last squared clicked
    playerClicks=[] 
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

            #Mouse Events    
            elif event.type == p.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected==(row,col):
                        sqSelected=()
                        playerClicks=[]
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                        if len(playerClicks)==1:
                            drawGameState(screen,gs,validMoves,sqSelected)
                    if len(playerClicks)==2:
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade=True
                                playerClicks = []
                                sqSelected=()
                                

                        if not moveMade:
                            playerClicks = [sqSelected]
            #KeyEvents
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    gs.undoMove()
                    moveMade=True


        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen,gs,validMoves,sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

#highlight squares
def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            #highlight squareselected
            s= p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            #highlight all squares possible to move to
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if  gs.board[move.endRow][move.endCol][0] == '-':
                        screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))
                        
            s.fill(p.Color('red'))        
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if  gs.board[move.endRow][move.endCol][0] != '-':
                        screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))
                        

#checkmate
def drawCheckmate(screen, w):
    winner = 'Black' if w else 'White'
    p.draw.rect(screen, (0, 0, 0), p.Rect(0, 0, WIDTH, HEIGHT))
    font = p.font.Font(None, 36)
    text = font.render(f"CHECKMATE -- {winner} wins", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    p.display.flip()
    
    



#Draw the graphics of current game state
def drawGameState(screen,gs,validMoves,sqSelected):
    if gs.checkMate:
        drawCheckmate(screen, gs.whiteToMove)
        return
    drawBoard(screen)
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen,gs.board)

def drawBoard(screen):
    colors=[p.Color('white'),p.Color('gray')]
    for r in range (DIMENSION):
        for c in range(DIMENSION):
            color=colors[((c+r)%2)]
            p.draw.rect(screen, color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawPieces(screen,board):
    for r in range (0,DIMENSION):
        for c in range(0,DIMENSION):
            piece=board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE,SQ_SIZE,SQ_SIZE))



if __name__=='__main__':
   main()








