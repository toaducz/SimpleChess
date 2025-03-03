import chess
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
        pygame_frame = pygame.transform.scale(pygame_frame, (100, 100))  # Điều chỉnh kích thước GIF
        gif_frames.append(pygame_frame)
    gif_frame_count = len(gif_frames)
except FileNotFoundError:
    print("Không tìm thấy file kobo.gif")
    gif_frames = []
    gif_frame_count = 0

# Khởi tạo bàn cờ và biến tỉ số
board = chess.Board()
white_wins = 0
black_wins = 0
game_ended = False
current_frame = 0  # Chỉ số khung hình hiện tại của GIF
frame_delay = 100  # Thời gian giữa các khung (ms)
last_frame_time = 0  # Thời điểm khung cuối cùng được cập nhật

def get_legal_moves(square):
    """Lấy danh sách các nước đi hợp lệ từ ô được chọn"""
    moves = [move for move in board.legal_moves if move.from_square == square]
    return moves

def draw_board(selected_square=None):
    """Vẽ bàn cờ, quân cờ và highlight các ô"""
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
    """Hiển thị tỉ số ở góc dưới bên phải"""
    score_text = f"Black: {black_wins} - White: {white_wins}"
    text = small_font.render(score_text, True, BLACK)
    screen.blit(text, (WINDOW_SIZE - 150, WINDOW_SIZE + 10))

def draw_replay_button(hovered=False):
    """Vẽ nút replay và highlight khi hover"""
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
    """Hiển thị thông báo và GIF khi trò chơi kết thúc"""
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

    # Hiển thị GIF trên thông báo
    if gif_frames:
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time >= frame_delay:
            current_frame = (current_frame + 1) % gif_frame_count
            last_frame_time = current_time
        gif_rect = gif_frames[current_frame].get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 60))
        screen.blit(gif_frames[current_frame], gif_rect)

    # Thông báo bên dưới GIF
    text = font.render(message, True, WHITE)
    text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 10))
    screen.blit(text, text_rect)

    # Nút chơi lại (Play Again)
    button_replay_rect = pygame.Rect(WINDOW_SIZE // 2 - 100, WINDOW_SIZE // 2 + 70, 200, 60)
    pygame.draw.rect(screen, BUTTON_COLOR, button_replay_rect)
    button_text = font.render("Play Again", True, WHITE)
    button_text_rect = button_text.get_rect(center=button_replay_rect.center)
    screen.blit(button_text, button_text_rect)

    return button_replay_rect

def reset_game():
    """Đặt lại bàn cờ để chơi ván mới"""
    global board, game_ended
    board = chess.Board()
    game_ended = False

def main():
    """Chạy trò chơi"""
    clock = pygame.time.Clock()
    selected_square = None
    running = True
    button_rect = pygame.Rect(10, WINDOW_SIZE, 40, 40)
    button_replay_rect = None
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        hovered = button_rect.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if not board.is_game_over():
                    if y < BOARD_SIZE:
                        col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
                        square = (7 - row) * 8 + col
                        
                        if selected_square is None:
                            if board.piece_at(square) and (board.turn == board.color_at(square)):
                                selected_square = square
                        else:
                            move = chess.Move(selected_square, square)
                            if move in board.legal_moves:
                                board.push(move)
                            selected_square = None
                if (button_replay_rect and button_replay_rect.collidepoint(x, y)) or button_rect.collidepoint(x, y):
                    reset_game()
                    selected_square = None
        
        draw_board(selected_square)
        draw_score()
        button_rect = draw_replay_button(hovered)
        
        if board.is_game_over():
            button_replay_rect = show_game_over()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()