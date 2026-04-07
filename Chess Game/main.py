import pygame
import sys
import os
import copy

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (245, 245, 245)
BLACK = (40, 40, 40)
BLUE = (106, 159, 181)

# Load piece images
piece_images = {}
def load_images():
    types = ["p", "r", "n", "b", "q", "k"]
    for color in ["w", "b"]:
        for t in types:
            name = f"{color}{t}"
            path = os.path.join("images", name + ".png")
            image = pygame.image.load(path)
            piece_images[name] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))

# Load sounds
move_sound = None
capture_sound = None
def load_sounds():
    global move_sound, capture_sound
    move_sound = pygame.mixer.Sound(os.path.join("sounds", "move.wav"))
    capture_sound = pygame.mixer.Sound(os.path.join("sounds", "capture.wav"))

# Create board
def create_board():
    board = [[None] * 8 for _ in range(8)]
    board[1] = ["bp"] * 8
    board[6] = ["wp"] * 8
    board[0] = ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"]
    board[7] = ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
    return board

# Draw board and pieces
def draw_board(win, board, selected):
    colors = [WHITE, BLACK]
    for r in range(ROWS):
        for c in range(COLS):
            color = colors[(r + c) % 2]
            pygame.draw.rect(win, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board[r][c]
            if piece:
                win.blit(piece_images[piece], (c * SQUARE_SIZE, r * SQUARE_SIZE))
    if selected:
        sr, sc = selected
        pygame.draw.rect(win, BLUE, (sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

# Helpers
def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def promote_pawn(board, r, c, color):
    promoting = True
    while promoting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    board[r][c] = color + 'q'
                    promoting = False
                elif event.key == pygame.K_r:
                    board[r][c] = color + 'r'
                    promoting = False
                elif event.key == pygame.K_b:
                    board[r][c] = color + 'b'
                    promoting = False
                elif event.key == pygame.K_n:
                    board[r][c] = color + 'n'
                    promoting = False

def get_raw_moves(board, r, c):
    piece = board[r][c]
    if not piece:
        return []
    color, p_type = piece[0], piece[1]
    moves = []

    directions = {
        'p': [(1, 0)],
        'r': [(1, 0), (-1, 0), (0, 1), (0, -1)],
        'b': [(1, 1), (-1, -1), (-1, 1), (1, -1)],
        'q': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)],
        'k': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)],
        'n': [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)],
    }

    if p_type == 'p':
        dir = -1 if color == 'w' else 1
        if in_bounds(r + dir, c) and not board[r + dir][c]:
            moves.append((r + dir, c))
        if (r == 6 and color == 'w') or (r == 1 and color == 'b'):
            if not board[r + dir][c] and not board[r + 2 * dir][c]:
                moves.append((r + 2 * dir, c))
        for dc in [-1, 1]:
            nr, nc = r + dir, c + dc
            if in_bounds(nr, nc) and board[nr][nc] and board[nr][nc][0] != color:
                moves.append((nr, nc))

    elif p_type in "rqb":
        for dr, dc in directions[p_type]:
            for i in range(1, 8):
                nr, nc = r + dr * i, c + dc * i
                if not in_bounds(nr, nc): break
                if not board[nr][nc]:
                    moves.append((nr, nc))
                elif board[nr][nc][0] != color:
                    moves.append((nr, nc))
                    break
                else:
                    break

    elif p_type in "kn":
        for dr, dc in directions[p_type]:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and (not board[nr][nc] or board[nr][nc][0] != color):
                moves.append((nr, nc))
    return moves

def is_in_check(board, color):
    king_pos = None
    for r in range(8):
        for c in range(8):
            if board[r][c] == color + 'k':
                king_pos = (r, c)
                break
    for r in range(8):
        for c in range(8):
            if board[r][c] and board[r][c][0] != color:
                if king_pos in get_raw_moves(board, r, c):
                    return True
    return False

def get_valid_moves(board, r, c):
    raw = get_raw_moves(board, r, c)
    valid = []
    for move in raw:
        new_board = copy.deepcopy(board)
        new_board[move[0]][move[1]] = new_board[r][c]
        new_board[r][c] = None
        if not is_in_check(new_board, board[r][c][0]):
            valid.append(move)
    return valid

def has_valid_moves(board, color):
    for r in range(8):
        for c in range(8):
            if board[r][c] and board[r][c][0] == color:
                if get_valid_moves(board, r, c):
                    return True
    return False

def is_game_over(board, color):
    return not has_valid_moves(board, color)

def apply_move(board, move):
    r1, c1, r2, c2 = move
    new_board = copy.deepcopy(board)
    new_board[r2][c2] = new_board[r1][c1]
    new_board[r1][c1] = None
    return new_board

def evaluate(board):
    score = 0
    values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 100}
    for row in board:
        for piece in row:
            if piece:
                val = values[piece[1]]
                score += val if piece[0] == 'w' else -val
    return score

def minimax(board, depth, maximizing):
    color = 'w' if maximizing else 'b'
    if depth == 0 or is_game_over(board, color):
        return evaluate(board), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for r in range(8):
            for c in range(8):
                if board[r][c] and board[r][c][0] == 'w':
                    for move in get_valid_moves(board, r, c):
                        new_board = apply_move(board, (r, c, move[0], move[1]))
                        eval, _ = minimax(new_board, depth - 1, False)
                        if eval > max_eval:
                            max_eval, best_move = eval, (r, c, move[0], move[1])
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for r in range(8):
            for c in range(8):
                if board[r][c] and board[r][c][0] == 'b':
                    for move in get_valid_moves(board, r, c):
                        new_board = apply_move(board, (r, c, move[0], move[1]))
                        eval, _ = minimax(new_board, depth - 1, True)
                        if eval < min_eval:
                            min_eval, best_move = eval, (r, c, move[0], move[1])
        return min_eval, best_move

def main():
    pygame.init()
    pygame.mixer.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess with AI")
    load_images()
    load_sounds()

    board = create_board()
    selected = None
    clock = pygame.time.Clock()
    running = True
    turn = 'w'
    winner = None

    while running:
        clock.tick(60)
        draw_board(win, board, selected)
        pygame.display.update()

        if not has_valid_moves(board, turn):
            if is_in_check(board, turn):
                winner = 'White' if turn == 'b' else 'Black'
                print(f"Checkmate! {winner} wins.")
            else:
                print("Stalemate!")
            pygame.time.delay(3000)
            running = False
            continue

        if turn == 'b':
            _, move = minimax(board, 2, False)
            if move:
                r1, c1, r2, c2 = move
                captured = board[r2][c2]
                board[r2][c2] = board[r1][c1]
                board[r1][c1] = None
                if captured:
                    capture_sound.play()
                else:
                    move_sound.play()
                if board[r2][c2][1] == 'p' and r2 == 7:
                    promote_pawn(board, r2, c2, 'b')
            turn = 'w'
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                r, c = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                if selected:
                    valid = get_valid_moves(board, *selected)
                    if (r, c) in valid:
                        captured = board[r][c]
                        board[r][c] = board[selected[0]][selected[1]]
                        board[selected[0]][selected[1]] = None
                        if captured:
                            capture_sound.play()
                        else:
                            move_sound.play()
                        if board[r][c][1] == 'p' and r == 0:
                            promote_pawn(board, r, c, 'w')
                        turn = 'b'
                        selected = None
                    else:
                        selected = None
                elif board[r][c] and board[r][c][0] == 'w':
                    selected = (r, c)

    # Show final message on window
    font = pygame.font.SysFont(None, 48)
    msg = "Stalemate!" if not winner else f"{winner} wins!"
    text = font.render(msg, True, (255, 0, 0))
    win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(3000)

if __name__ == "__main__":
    main()
