import pygame
import sys
import os
from pacman.core.grid import Grid
from pacman.core.rules import Rules
from pacman.core.state import GameState
from pacman.ui.renderer import Renderer

from pacman.agents.manual_agent import ManualAgent
from pacman.agents.auto_agent import AutoAgent

CELL_SIZE = 30
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets")

class ModeSelectionScreen:
    """
    Giao diện chọn chế độ chơi đẹp hơn, có hình ảnh và hiệu ứng.
    """
    def __init__(self, width, height):
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pacman - Play Mode")

        # Font
        self.font_title = pygame.font.Font(None, 90)
        self.font_button = pygame.font.Font(None, 48)
        self.font_note = pygame.font.Font(None, 28)

        # Màu sắc
        self.bg_color = (10, 10, 30)
        self.button_color = (255, 255, 0)
        self.hover_color = (255, 180, 0)
        self.text_color = (0, 0, 0)
        self.white = (255, 255, 255)

        # Tạo đường dẫn đến folder chứa ảnh
        ghost_dir = os.path.join(ASSETS_DIR, "ghost_images")
        pacman_path = os.path.join(ASSETS_DIR, "player_images")

        # Load hình ảnh
        self.pacman_img = pygame.image.load(os.path.join(pacman_path, "1.png"))
        self.exit_img = pygame.image.load(os.path.join(pacman_path, "exitgate.png"))
        self.ghost_imgs = [
            pygame.image.load(os.path.join(ghost_dir, "blue.png")),
            pygame.image.load(os.path.join(ghost_dir, "orange.png")),
            pygame.image.load(os.path.join(ghost_dir, "pink.png")),
            pygame.image.load(os.path.join(ghost_dir, "red.png")),
        ]

        # Resize ảnh
        self.pacman_img = pygame.transform.scale(self.pacman_img, (80, 80))
        self.exit_img = pygame.transform.scale(self.exit_img, (80, 80))
        self.ghost_imgs = [pygame.transform.scale(g, (50, 50)) for g in self.ghost_imgs]

        # Nút chọn chế độ
        self.button_manual = pygame.Rect(self.screen_width//2 - 150, 260, 300, 70)
        self.button_auto = pygame.Rect(self.screen_width//2 - 150, 360, 300, 70)

    def draw_button(self, rect, text, is_hover):
        """Vẽ nút có hiệu ứng hover."""
        color = self.hover_color if is_hover else self.button_color
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        pygame.draw.rect(self.screen, self.white, rect, 3, border_radius=15)
        text_surface = self.font_button.render(text, True, self.text_color)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def run(self):
        clock = pygame.time.Clock()
        while True:
            mouse_pos = pygame.mouse.get_pos()
            hover_manual = self.button_manual.collidepoint(mouse_pos)
            hover_auto = self.button_auto.collidepoint(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise Exception("QUIT")
                
                # bấm esc
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        raise Exception("QUIT")
                
                # điều hướng
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hover_manual:
                        return ManualAgent
                    elif hover_auto:
                        return AutoAgent

            # Nền mờ + đồ họa
            self.screen.fill(self.bg_color)
            self.screen.blit(self.exit_img, (self.screen_width//2 + 40, 120))
            self.screen.blit(self.pacman_img, (self.screen_width//2 - 120, 120))
            ghost_w, ghost_h = 50, 50 # kích thước của ma
            ghost_positions = [
                (30, 50),  # trên trái
                (self.screen_width - ghost_w - 30, 50),  # trên phải
                (20, self.screen_height - ghost_h - 20),  # dưới trái
                (self.screen_width - ghost_w - 20, self.screen_height - ghost_h - 20),  # dưới phải
            ]

            for ghost, pos in zip(self.ghost_imgs, ghost_positions):
                self.screen.blit(ghost, pos)


            # Tiêu đề
            title_surface = self.font_title.render("PACMAN", True, self.button_color)
            self.screen.blit(title_surface, title_surface.get_rect(center=(self.screen_width//2, 60)))

            # Nút
            self.draw_button(self.button_manual, " Manual Mode", hover_manual)
            self.draw_button(self.button_auto, " Auto Mode", hover_auto)

            # Ghi chú nhỏ
            note = self.font_note.render("Press ESC to exit", True, (180, 180, 180))
            self.screen.blit(note, note.get_rect(center=(self.screen_width//2, 480)))

            pygame.display.flip()
            clock.tick(60)

class GameEngine:
    def __init__(self, layout_file, agent_class):

        # Khởi tạo Grid và GameState
        self.grid = Grid(layout_file)

        self.initial_ghosts = tuple() # TODO: Khởi tạo trạng thái ban đầu của Ghosts
        self.game_state = GameState.get_initial_state(self.grid, self.initial_ghosts)
        
        # Cấu hình màn hình
        self.screen_width = self.grid.cols * CELL_SIZE
        self.screen_height = (self.grid.rows + 2) * CELL_SIZE
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pacman")

        # Khởi tạo Renderer
        self.renderer = Renderer(self.screen, self.grid)
        
        # Khởi tạo Agent
        self.agent = agent_class() 
        self.pacman_direction = 0 # 0: Phải, 90: Lên, 180: Trái, 270: Xuống
        self.game_status = 'running' # 'running', 'win', 'lose'

        # TODO: Implement Rules (Logic chuyển trạng thái)
        # self.rules = Rules(self.grid)

        # Khởi tạo Rules
        self.rules = Rules(self.grid) # <-- THÊM DÒNG NÀY
        self.clock = pygame.time.Clock()

    def _get_action_from_manual(self, event):
        """Xử lý input bàn phím cho chế độ thủ công."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                return (-1, 0), 90 # (dr, dc), direction
            elif event.key == pygame.K_DOWN:
                return (1, 0), 270
            elif event.key == pygame.K_LEFT:
                return (0, -1), 180
            elif event.key == pygame.K_RIGHT:
                return (0, 1), 0
        return None, self.pacman_direction

    def reset_game(self):
            """
            Tải lại game về trạng thái ban đầu.
            """
            print("Resetting game...")
            # Tải lại grid từ file (để khôi phục tường đã ăn)
            self.grid = Grid(self.grid.layout_file) 
            
            # Tạo lại state ban đầu
            self.game_state = GameState.get_initial_state(self.grid, self.initial_ghosts)
            
            # Cập nhật tham chiếu grid cho rules và renderer
            self.rules.grid = self.grid
            self.renderer.grid = self.grid
            
            # Reset các biến trạng thái game
            self.pacman_direction = 0
            self.game_status = 'running'

    def run(self):
        running = True
        while running:
            
            # --- Xử lý sự kiện (Input) ---
            action = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu' # <-- Trả về 'menu' để main.py xử lý
                    
                    if self.game_status != 'running':
                        if event.key == pygame.K_r:
                            self.reset_game()
                            continue # Bỏ qua phần còn lại của vòng lặp event

                    if self.game_status == 'running':
                        if self.agent.__class__.__name__ == 'ManualAgent':
                            # Chế độ thủ công
                            move_vector, new_direction = self._get_action_from_manual(event)
                            if move_vector:
                                action = move_vector 
                                self.pacman_direction = new_direction

            # --- Cập nhật Logic Game (Transition) ---
            if self.game_status == 'running':
                
                # Cập nhật hoạt ảnh (chỉ cho GUI)
                self.renderer.update_animation()
                self.renderer.update_animation_magical_pie()

                if self.agent.__class__.__name__ == 'AutoAgent':
                    # Chế độ tự động: Lấy hành động từ A*
                    action = self.agent.get_action(self.game_state)
                    # TODO: Cập nhật self.pacman_direction dựa trên action A* của AutoAgent
                    
                    # Tạm thời, nếu Agent A* trả về action, ta có thể suy ra hướng xoay
                    if action:
                        dr, dc = action
                        if dr == -1 and dc == 0: self.pacman_direction = 90  # Lên
                        elif dr == 1 and dc == 0: self.pacman_direction = 270 # Xuống
                        elif dr == 0 and dc == -1: self.pacman_direction = 180 # Trái
                        elif dr == 0 and dc == 1: self.pacman_direction = 0   # Phải
                
                # --- APPLY ACTION: Dùng Rules để tính GameState tiếp theo ---
                if action:
                    # Gọi Rules để nhận trạng thái mới. 
                    # Logic va chạm, ăn thức ăn/bánh, và Power Mode đã được xử lý bên trong rules.py
                    self.game_state = self.rules.get_successor(self.game_state, action)
                    
                # --- KIỂM TRA ĐIỀU KIỆN THẮNG ---
                food_left = len(self.game_state.food_left)
                at_exit = self.game_state.pacman_pos == self.grid.exitgate_pos
                
                # Điều kiện thắng: Ăn gần hết thức ăn (<= 6) VÀ Pacman đang ở cổng thoát
                # (Sử dụng <= 6 theo logic cũ của bạn)
                if food_left <= 6 and at_exit:
                    self.game_status = 'win'

            # --- VẼ ---
            self.renderer.draw_all(self.game_state, self.pacman_direction)

            # Vẽ màn hình thắng/thua nếu cần
            if self.game_status == 'win':
                self.renderer.draw_win_screen(self.game_state.step_count)

            # Cập nhật màn hình MỘT LẦN DUY NHẤT (Đã chuyển từ renderer.draw_all ra ngoài)
            pygame.display.flip() 

            self.clock.tick(60) 

        pygame.quit()
        sys.exit()