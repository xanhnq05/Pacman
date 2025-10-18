import os
import sys
import pygame

from pacman.ui.game import GameEngine, ModeSelectionScreen
from pacman.agents.manual_agent import ManualAgent
from pacman.agents.auto_agent import AutoAgent

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500

def parse_args_and_get_config():
    """
    Hàm này sẽ chọn chế độ chơi -> trả về đường dẫn của file và agent class(manual or auto mode).
    """
    selection_screen = ModeSelectionScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # selection_screen.run() sẽ trả về agent_class hoặc ném ra exception nếu thoát
    agent_class = selection_screen.run()
    
    layout_path = 'data/layout.txt' # Layout mặc định
    return layout_path, agent_class

def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # hiển thị screen ở giữa màn hình
    pygame.init()
    
    game_mode = 'menu'
    
    while True:
        if game_mode == 'menu':
            # --- Chạy màn hình chọn mode ---
            try:
                layout_path, agent_class = parse_args_and_get_config()
                game_mode = 'running' # Chuyển sang chế độ chạy game

            except Exception:
                print("Player has exit.")
                break

        elif game_mode == 'running':
            # --- Chạy Game Engine ---
            print("\n-----------------------------------------")
            print(f"Choosen mode: {agent_class.__name__}")
            print("-----------------------------------------")

            game = GameEngine(
                layout_file=layout_path, 
                agent_class=agent_class
            )
            
            try:
                # game.run() sẽ trả về status: 'menu' (nếu nhấn ESC) hoặc 'quit'
                run_status = game.run()
            except Exception as e:
                print(f"Error ocurrs when loading: {e}")
                run_status = 'quit' 

            # Kiểm tra trạng thái trả về từ GameEngine.run()
            if run_status == 'menu':
                game_mode = 'menu' # Quay lại màn hình chọn chế độ
            elif run_status == 'quit':
                break

    print("\n-----------------------------------------")
    print("The end!")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()