# main.py
import sys
import pygame

# Import các thành phần đã phân tách
from pacman.ui.game import GameEngine, ModeSelectionScreen
from pacman.agents.manual_agent import ManualAgent
from pacman.agents.auto_agent import AutoAgent
# Đảm bảo bạn có thư mục data/ và file layout.txt

# Kích thước cố định cho màn hình chọn chế độ
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500

def parse_args_and_get_config():
    pygame.init()
    
    # Tạo màn hình chọn chế độ
    selection_screen = ModeSelectionScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # --- Vòng lặp chọn chế độ ---
    try:
        agent_class = selection_screen.run()
    except Exception as e:
        # Xử lý nếu người dùng thoát game ngay tại màn hình chọn chế độ
        print("Người dùng đã thoát khỏi màn hình chọn chế độ.")
        pygame.quit()
        sys.exit()

    # --- Sau khi đã chọn chế độ ---
    layout_path = 'data/layout.txt' # Layout mặc định
    return layout_path, agent_class

def main():
    layout_path, agent_class = parse_args_and_get_config()
    
    print("\n-----------------------------------------")
    print("Waiting...")
    
    # Khởi tạo Game Engine (nó sẽ tự động khởi tạo Grid, State, Renderer, và Agent)
    game = GameEngine(
        layout_file=layout_path, 
        agent_class=agent_class
    )
    
    # Bắt đầu Game
    try:
        game.run()
    except Exception as e:
        print(f"Erorr ocurrs when loading: {e}")
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()
