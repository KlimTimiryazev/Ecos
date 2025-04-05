class GameState():
    def __init__(self):
        # доска 8 на 8 
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRockMoves, 'N': self.getKnightMoves,  #вызов функций для генерации ходов
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
    '''
    принимает ход в качестве параметра и выполняет его(кроме рокировки и взятия на проходе и двойной ход пешки)'''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # сохраняем ход, МОЖЕМ сделать ОТМЕНУ
        self.whiteToMove = not self.whiteToMove # меняем игроков

        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

    #Имитация реального перемещения фигуры на доске с обновлением всей необходимой информации о состоянии 




    '''отмена хода'''
    def undoMove(self):
        if len(self.moveLog) != 0: #берет последжний ход из списка
            move = self.moveLog.pop() # удаляем последний ход
            self.board[move.startRow][move.startCol] = move.pieceMoved 
            self.board[move.endRow][move.endCol] = move.pieceCaptured # возвращаем фигуру на место
            self.whiteToMove = not self.whiteToMove # меняем игроков
            # обновление позиции короля если нужно
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)



    '''все ходы с учетом проверок'''
    def getValidMoves(self):
        #1.) сгенерировать все возможные ходы (без учета шахов)
        moves = self.getAllPossibleMoves() #Возвращает список только легальных ходов.
    #2.) для каждого хода, сделать этот ход (временно, на доске)
        # НЕПРАВИЛЬНЫЙ ВАРИАНТ (как у вас сейчас):
        # ПРАВИЛЬНЫЙ ВАРИАНТ:
        for i in range(len(moves)-1, -1, -1):
            current_move = moves[i] # Сохраним ход для возможного удаления
            self.makeMove(current_move) # 1. Сделали ход (например, ЧЕРНЫХ). self.whiteToMove стал TRUE (ход БЕЛЫХ).
            
            # 2. Временно возвращаем ход ЧЕРНЫМ, чтобы проверить ИХ короля.
            self.whiteToMove = not self.whiteToMove # self.whiteToMove стал FALSE.
            
            # 3. Вызываем self.inCheck(). Теперь он проверит ЧЕРНОГО короля.
            in_check_after_move = self.inCheck() 
            
            # 4. Возвращаем ход обратно БЕЛЫМ, чтобы undoMove сработал правильно.
            self.whiteToMove = not self.whiteToMove # self.whiteToMove снова TRUE.
                
            # 5. Если ЧЕРНЫЙ король оказался под шахом ПОСЛЕ хода черных...
            if in_check_after_move:  
                # ...то ход ЧЕРНЫХ был нелегальным, удаляем его.
                moves.remove(current_move) 
                    
            self.undoMove() # 6. Отменяем ход. self.whiteToMove вернется к FALSE (ход ЧЕРНЫХ).

        # ... (далее проверка на мат/пат, которая теперь должна работать корректнее) ...
        if len(moves) == 0: # Если валидных ходов не осталось
            # Проверяем, находится ли ТЕКУЩИЙ игрок под шахом СЕЙЧАС (до хода)
            if self.inCheck(): 
                self.checkMate = True
            else:
                self.staleMate = True
        else: # Иначе сбрасываем флаги
            self.checkMate = False
            self.staleMate = False

        return moves 

    def inCheck(self):  ##Проверяет, находится ли король текущего игрока под атакой.
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
 
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # Переключаемся на противника
        oppMoves = self.getAllPossibleMoves()    # Генерируем его ходы
        self.whiteToMove = not self.whiteToMove  # Возвращаемся к исходному игроку
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # Если ход противника атакует (r, c)
                #self.whiteToMove = not self.whiteToMove
                return True
        return False

    
        
    
    '''все возможные ходы без проверок'''
    def getAllPossibleMoves(self):  #Генерирует список всех ходов, которые фигуры текущего игрока могут сделать по правилам их движения, игнорируя шахи.
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) 
        return moves

    '''
    все ходы для пешек и добавим их в список'''
    def getPawnMoves(self, r, c, moves):  
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c - 1 >= 0: #захваты слева
                if self.board[r-1][c-1][0] == 'b': #захват чужой пешки
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: #захваты справа
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))

        else: # black
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c - 1 >= 0: # захваты слева
                if self.board[r+1][c-1][0] == 'w': # захват чужой пешки
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c + 1 <= 7: # захваты справа
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
        #добавим повышение пешек


    '''
    все ходы для ладьи'''
    def getRockMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # вверх, влево, вниз, вправо
        enemyColor = 'b' if self.whiteToMove else 'w' # если ход белых то черные - противники
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # на доске
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #дружеская фигура invalid
                        break
                else: #за пределы доски
                    break



    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                   


    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  
                        break
                else:  
                    break


    def getQueenMoves(self, r, c, moves):  #абстракция
        self.getRockMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)


    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1),(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # Check if the move is on the board
                endPiece = self.board[endRow][endCol]
                if endPiece == '--':  # Empty square
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                elif endPiece[0] != allyColor:  # Capture enemy piece
                    moves.append(Move((r, c), (endRow, endCol), self.board))








class Move():


    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4,
                   '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                   'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol] 
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        print(self.moveID)
    '''
    переопределение метода equals''' 
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

        
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]