import pygame as p
from ChessEngine import GameState, Move 


# Константы
WIDTH = HEIGHT = 400
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Функция для загрузки изображений
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        try:
            IMAGES[piece] = p.transform.scale(p.image.load('c:/VS CODE PY/Chess/images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))
            print(f"Загружено изображение: {piece}")
        except Exception as e:
            print(f"Ошибка при загрузке {piece}: {e}")

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # Флаг для генерации ходов только после того, как ход сделан

    loadImages()
    running = True
    sqSelected = ()  # хранит координаты выбранной клетки (row, col)
    playerClicks = []  # хранит клики игрока [(start_row, start_col), (end_row, end_col)]

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # обработчик мыши
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # получаем позицию мыши (x, y)
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                # Проверяем, не кликнули ли повторно по той же клетке или за пределами доски
                if sqSelected == (row, col) or row >= DIMENSION or col >= DIMENSION:
                    sqSelected = ()  # сбрасываем выделение
                    playerClicks = []  # сбрасываем клики
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) # добавляем первый или второй клик

                # Если сделано два клика
                if len(playerClicks) == 2:
                    # 1. Создаем объект хода
                    move = Move(playerClicks[0], playerClicks[1], gs.board)
                    print(f"Попытка хода: {move.getChessNotation()}") # Отладочный вывод

                    # 2. Проверяем, валиден ли ход
                    # Важно: Проверка 'in' сработает, только если __eq__ в классе Move реализован корректно
                    # и validMoves содержит объекты Move.
                    move_is_valid = False
                    for valid_move in validMoves:
                         # Используем переопределенный __eq__ для сравнения ходов
                        if move == valid_move:
                            move_is_valid = True
                            break # Нашли валидный ход, выходим из цикла

                    if move_is_valid:
                        # 3. Если ход валидный, выполняем его
                        gs.makeMove(move)
                        print("Ход выполнен.")
                        moveMade = True # Устанавливаем флаг, чтобы пересчитать ходы
                        sqSelected = ()  # сбрасываем выделение
                        playerClicks = []  # сбрасываем клики
                    else:
                        ###playerClicks = [sqSelected]
                        # 4. Если ход невалидный
                        print("Невалидный ход.")
                        if playerClicks:
                            sqSelected = playerClicks[0]
                        # Оставляем выбранной первую клетку, чтобы игрок мог выбрать другую конечную клетку
                            playerClicks = [playerClicks[0]]
                        else:
                            sqSelected = ()
                            playerClicks = []
            
                        # sqSelected уже содержит координаты первой клетки

            # обработка с помощью клавиатуры
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # отмена хода когда z зажата
                    gs.undoMove()
                    print("Ход отменен.")
                    moveMade = True # Нужно пересчитать ходы после отмены
                    sqSelected = () # Сбрасываем выделение после отмены
                    playerClicks = []
                
                    


        # Пересчитываем валидные ходы только если ход был сделан (или отменен)
        if moveMade:
            validMoves = gs.getValidMoves()
            print(f"Сгенерировано {len(validMoves)} валидных ходов.") # Отладка
            moveMade = False # Сбрасываем флаг

        drawGameState(screen, gs, validMoves, sqSelected)  # отрисовка состояния игры

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Белые выиграли')
            else:
                drawText(screen, 'Черные выиграли')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Ничья')
            
        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # выделяем выбранную клетку
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Прозрачность
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # выделяем валидные ходы
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)  # выделяем клетки  
    drawPieces(screen, gs.board)  
    

# Функция для отрисовки доски
def drawBoard(screen):
    colors = [p.Color('thistle'), p.Color('darkviolet')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    

# Функция для отрисовки фигур
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
               
    
def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color('black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH // 2 - textObject.get_width() // 2, HEIGHT // 2 - textObject.get_height() // 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('green'))
    screen.blit(textObject, textLocation.move(2, 2))  # Отрисовка тени текста

if __name__ == '__main__':
    main()



