import chess
import chess.engine
import pygame
from PIL import Image
import io

# Khởi tạo Pygame
pygame.init()

# Cài đặt kích thước
SQUARE_SIZE = 60
BOARD_SIZE = SQUARE_SIZE * 8
WINDOW_SIZE = BOARD_SIZE

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (245, 222, 179)
DARK_BROWN = (139, 69, 19)
HIGHLIGHT = (255, 255, 0, 100)  
SELECTED = (0, 255, 0, 100)     
ATTACKED = (255, 0, 0, 100)     
BUTTON_COLOR = (0, 128, 255)    
BUTTON_HOVER = (0, 255, 0, 100)

# Tạo cửa sổ
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 40))
pygame.display.set_caption("Chess Game")

# Font
font = pygame.font.SysFont("Arial", 40, bold=True)
small_font = pygame.font.SysFont("Arial", 20, bold=True)

# Giả lập hình ảnh quân cờ
piece_images = {}
try:
    piece_images = {
        "P": pygame.image.load("pieces/wP.png"), "N": pygame.image.load("pieces/wN.png"),
        "B": pygame.image.load("pieces/wB.png"), "R": pygame.image.load("pieces/wR.png"),
        "Q": pygame.image.load("pieces/wQ.png"), "K": pygame.image.load("pieces/wK.png"),
        "p": pygame.image.load("pieces/bP.png"), "n": pygame.image.load("pieces/bN.png"),
        "b": pygame.image.load("pieces/bB.png"), "r": pygame.image.load("pieces/bR.png"),
        "q": pygame.image.load("pieces/bQ.png"), "k": pygame.image.load("pieces/bK.png"),
    }
    for key in piece_images:
        piece_images[key] = pygame.transform.scale(piece_images[key], (SQUARE_SIZE, SQUARE_SIZE))
except FileNotFoundError:
    print("Không tìm thấy file ảnh quân cờ, dùng text thay thế.")

# Tải icon replay
try:
    replay_icon = pygame.image.load("button/replay.png")
    replay_icon = pygame.transform.scale(replay_icon, (40, 40))
except FileNotFoundError:
    print("Không tìm thấy file replay.png, dùng mặc định.")

# Tải và xử lý GIF
try:
    gif = Image.open("kobo.gif")
    gif_frames = []
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = gif.convert("RGBA")
        frame_bytes = io.BytesIO()
        frame_image.save(frame_bytes, format="PNG")
        frame_bytes.seek(0)
        pygame_frame = pygame.image.load(frame_bytes)
        pygame_frame = pygame.transform.scale(pygame_frame, (100, 100))
        gif_frames.append(pygame_frame)
    gif_frame_count = len(gif_frames)
except FileNotFoundError:
    print("Không tìm thấy file kobo.gif")
    gif_frames = []
    gif_frame_count = 0

# Khởi tạo biến toàn cục
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2.exe")
white_wins = 0
black_wins = 0
game_ended = False
current_frame = 0
frame_delay = 100
last_frame_time = 0
game_started = False

# Cấu hình độ khó
DIFFICULTY = {
    "Easy": {"Skill Level": 1, "depth": 3, "elo": "~500"},
    "Normal": {"Skill Level": 5, "depth": 5, "elo": "~1000"},
    "Hard": {"Skill Level": 10, "depth": 7, "elo": "~1500"}
}

def draw_difficulty_menu():
    screen.fill(WHITE)
    title = font.render("Select Difficulty", True, BLACK)
    screen.blit(title, (WINDOW_SIZE // 2 - title.get_width() // 2, 100))

    easy_rect = pygame.Rect(WINDOW_SIZE // 2 - 100, 200, 200, 60)
    pygame.draw.rect(screen, BUTTON_COLOR, easy_rect)
    easy_text = font.render("Easy (~500)", True, WHITE)
    screen.blit(easy_text, (easy_rect.centerx - easy_text.get_width() // 2, easy_rect.centery - easy_text.get_height() // 2))

    normal_rect = pygame.Rect(WINDOW_SIZE // 2 - 100, 280, 200, 60)
    pygame.draw.rect(screen, BUTTON_COLOR, normal_rect)
    normal_text = font.render("Normal (~1000)", True, WHITE)
    screen.blit(normal_text, (normal_rect.centerx - normal_text.get_width() // 2, normal_rect.centery - normal_text.get_height() // 2))

    hard_rect = pygame.Rect(WINDOW_SIZE // 2 - 100, 360, 200, 60)
    pygame.draw.rect(screen, BUTTON_COLOR, hard_rect)
    hard_text = font.render("Hard (~1500)", True, WHITE)
    screen.blit(hard_text, (hard_rect.centerx - hard_text.get_width() // 2, hard_rect.centery - hard_text.get_height() // 2))

    return easy_rect, normal_rect, hard_rect

def get_legal_moves(square):
    return [move for move in board.legal_moves if move.from_square == square]

def draw_board(selected_square=None):
    screen.fill(WHITE)
    for row in range(8):
        for col in range(8):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    if selected_square is not None:
        col, row = selected_square % 8, 7 - (selected_square // 8)
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(SELECTED)
        screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        legal_moves = get_legal_moves(selected_square)
        for move in legal_moves:
            to_square = move.to_square
            to_col, to_row = to_square % 8, 7 - (to_square // 8)
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            if board.piece_at(to_square) and board.color_at(to_square) != board.turn:
                highlight_surface.fill(ATTACKED)
            else:
                highlight_surface.fill(HIGHLIGHT)
            screen.blit(highlight_surface, (to_col * SQUARE_SIZE, to_row * SQUARE_SIZE))

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            col, row = square % 8, 7 - (square // 8)
            if piece_images:
                screen.blit(piece_images[piece.symbol()], (col * SQUARE_SIZE, row * SQUARE_SIZE))
            else:
                text = font.render(piece.symbol(), True, BLACK)
                screen.blit(text, (col * SQUARE_SIZE + 20, row * SQUARE_SIZE + 10))

def draw_score():
    score_text = f"Black: {black_wins} - White: {white_wins}"
    text = small_font.render(score_text, True, BLACK)
    screen.blit(text, (WINDOW_SIZE - 150, WINDOW_SIZE + 10))

def draw_replay_button(hovered=False):
    button_rect = pygame.Rect(10, WINDOW_SIZE, 40, 40)
    if hovered:
        hover_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        hover_surface.fill(BUTTON_HOVER)
        screen.blit(hover_surface, (10, WINDOW_SIZE))
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
    if 'replay_icon' in globals():
        screen.blit(replay_icon, (10, WINDOW_SIZE))
    return button_rect

def show_game_over():
    global white_wins, black_wins, game_ended, current_frame, last_frame_time
    
    if not game_ended:
        result = board.result()
        if result == "1-0":
            white_wins += 1
        elif result == "0-1":
            black_wins += 1
        game_ended = True
    
    result = board.result()
    if result == "1-0":
        message = "White Won!"
    elif result == "0-1":
        message = "Black Won!"
    elif result == "1/2-1/2":
        message = "Draw!"
    else:
        message = "Game Over!"
    
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    if gif_frames:
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time >= frame_delay:
            current_frame = (current_frame + 1) % gif_frame_count
            last_frame_time = current_time
        gif_rect = gif_frames[current_frame].get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 60))
        screen.blit(gif_frames[current_frame], gif_rect)

    text = font.render(message, True, WHITE)
    text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 10))
    screen.blit(text, text_rect)

    button_replay_rect = pygame.Rect(WINDOW_SIZE // 2 - 100, WINDOW_SIZE // 2 + 70, 200, 60)
    pygame.draw.rect(screen, BUTTON_COLOR, button_replay_rect)
    button_text = font.render("Play Again", True, WHITE)
    button_text_rect = button_text.get_rect(center=button_replay_rect.center)
    screen.blit(button_text, button_text_rect)

    return button_replay_rect

def reset_game():
    global board, game_ended, game_started
    board = chess.Board()
    game_ended = False
    game_started = False

def computer_move(difficulty):
    if not board.is_game_over() and board.turn == chess.BLACK:
        engine.configure({"Skill Level": DIFFICULTY[difficulty]["Skill Level"]})
        result = engine.play(board, chess.engine.Limit(depth=DIFFICULTY[difficulty]["depth"], time=0.1))
        board.push(result.move)

def main():
    clock = pygame.time.Clock()
    selected_square = None
    running = True
    button_rect = pygame.Rect(10, WINDOW_SIZE, 40, 40)
    button_replay_rect = None
    difficulty = None
    global board, game_ended, game_started
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        hovered = button_rect.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if not game_started:
                    easy_rect, normal_rect, hard_rect = draw_difficulty_menu()
                    if easy_rect.collidepoint(x, y):
                        difficulty = "Easy"
                        game_started = True
                    elif normal_rect.collidepoint(x, y):
                        difficulty = "Normal"
                        game_started = True
                    elif hard_rect.collidepoint(x, y):
                        difficulty = "Hard"
                        game_started = True
                else:
                    if not board.is_game_over():
                        if y < BOARD_SIZE:
                            col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
                            square = (7 - row) * 8 + col
                            
                            if selected_square is not None:
                                move = chess.Move(selected_square, square)
                                if move in board.legal_moves:  # Nếu nước đi hợp lệ (bao gồm ăn quân)
                                    board.push(move)
                                    selected_square = None
                                    computer_move(difficulty)
                                elif board.piece_at(square) and board.color_at(square) == chess.WHITE:
                                    # Chỉ chọn lại nếu là quân của mình (Trắng)
                                    selected_square = square
                            else:
                                # Chỉ tô xanh nếu nhấp vào quân của mình (Trắng)
                                if board.piece_at(square) and board.color_at(square) == chess.WHITE:
                                    selected_square = square
                    if (button_replay_rect and button_replay_rect.collidepoint(x, y)) or button_rect.collidepoint(x, y):
                        reset_game()
                        selected_square = None
        
        if not game_started:
            draw_difficulty_menu()
        else:
            draw_board(selected_square)
            draw_score()
            button_rect = draw_replay_button(hovered)
            if board.is_game_over():
                button_replay_rect = show_game_over()
        
        pygame.display.flip()
        clock.tick(60)
    
    engine.quit()
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Lỗi: {e}")
        engine.quit()
        pygame.quit()