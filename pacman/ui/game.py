import pygame
import sys
import os
from pacman.core.grid import Grid
from pacman.core.rules import Rules
from pacman.core.state import GameState
from pacman.ui.renderer import Renderer

from pacman.agents.manual_agent import ManualAgent
from pacman.agents.auto_agent import AutoAgent

CELL_SIZE = 20
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets")

class ModeSelectionScreen:
    """
    Giao diện chọn chế độ chơi.
    """
    def __init__(self, width, height):
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pacman - Mode")

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
        try:
            print(f"Initializing game with layout: {layout_file}")
            
            # Khởi tạo Grid và GameState
            self.grid = Grid(layout_file)
            print(f"Grid loaded: {self.grid.rows}x{self.grid.cols}")

            self.initial_ghosts = tuple() # TODO: Khởi tạo trạng thái ban đầu của Ghosts
            self.game_state = GameState.get_initial_state(self.grid)        
            print(f"Game state initialized")

            # Cấu hình màn hình
            self.screen_width = self.grid.cols * CELL_SIZE
            self.screen_height = (self.grid.rows + 2) * CELL_SIZE
            print(f"Screen size: {self.screen_width}x{self.screen_height}")
            
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Pacman")
            print("Screen created successfully")

            # Khởi tạo Rules
            self.rules = Rules(self.grid)
            print("Rules initialized")
            
            # Khởi tạo Renderer
            self.renderer = Renderer(self.screen, self.grid)
            print("Renderer initialized")
            
            # Khởi tạo Agent
            if agent_class.__name__ == 'AutoAgent':
                # Allow choosing heuristic type for AutoAgent
                heuristic_type = "tsp_maze"  # Default to best heuristic
                self.agent = agent_class(self.grid, self.rules, heuristic_type)
                print(f"AutoAgent using {heuristic_type} heuristic")
            else:
                self.agent = agent_class()
            print(f"Agent initialized: {agent_class.__name__}")
            
            self.game_status = 'running' # 'running', 'win', 'lose'
            self.clock = pygame.time.Clock()
            print("Game initialization completed successfully")
            
        except Exception as e:
            print(f"Error during game initialization: {e}")
            import traceback
            traceback.print_exc()
            raise e

    def _update_screen_after_rotation(self):
        """
        Cập nhật màn hình sau khi mê cung bị xoay.
        """
        # Cập nhật kích thước màn hình
        self.screen_width = self.grid.cols * CELL_SIZE
        self.screen_height = (self.grid.rows + 2) * CELL_SIZE
        
        # Tạo màn hình mới với kích thước mới
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pacman")
        
        # Cập nhật renderer với grid mới và screen mới
        self.renderer.update_grid(self.grid)
        self.renderer.update_screen(self.screen)

    def reset_game(self):
            """
            Tải lại game về trạng thái ban đầu.
            """
            print("Resetting game...")
            # Reset mê cung về trạng thái ban đầu (không xoay)
            self.grid.reset_to_initial_state()
            
            # Tạo lại state ban đầu
            self.game_state = GameState.get_initial_state(self.grid)
            
            # Cập nhật tham chiếu grid cho rules và renderer
            self.rules.grid = self.grid
            self.renderer.grid = self.grid
            
            # Cập nhật màn hình sau khi reset
            self._update_screen_after_rotation()
            
            # Reset các biến trạng thái game
            self.game_status = 'running'
            
            # Reset biến xoay mê cung
            if hasattr(self, '_last_rotation_step'):
                delattr(self, '_last_rotation_step')

    def run(self):
        running = True
        while running:
                        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit' 

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu' # <-- Trả về 'menu'
                    
                    if self.game_status != 'running': 
                        if event.key == pygame.K_r: 
                            self.reset_game() 
                            continue 

                # --- GỬI EVENT CHO AGENT ---
                # Luôn gửi event cho agent để xử lí hành động
                if self.game_status == 'running': 
                    self.agent.process_event(event)

            # --- Cập nhật Logic Game (Transition) ---
            if self.game_status == 'running': 
                self.renderer.update_animation() 
                self.renderer.update_animation_magical_pie()
                self.renderer.update_teleport_animation() 

                # --- LẤY HÀNH ĐỘNG TỪ AGENT (SAU KHI ĐÃ XỬ LÝ EVENTS) ---
                action = self.agent.get_action(self.game_state)
                
                # --- KIỂM TRA VA CHẠM TRƯỚC KHI DI CHUYỂN ---
                # LUÔN LUÔN kiểm tra va chạm - bất cứ khi nào chạm Ghost đều thua
                if action:
                    pacman_pos = self.game_state.pacman.pos
                    dr, dc = action
                    new_pacman_pos = (pacman_pos[0] + dr, pacman_pos[1] + dc)
                    
                    # Kiểm tra va chạm với từng Ghost
                    for ghost in self.game_state.ghosts:
                        # Tính toán vị trí mới của Ghost (nếu Ghost di chuyển)
                        new_ghost = ghost.get_updated_state(self.grid)
                        new_ghost_pos = new_ghost.pos
                        
                        # Kiểm tra các trường hợp va chạm (LUÔN LUÔN):
                        # 1. Pacman di chuyển đến vị trí hiện tại của Ghost
                        if new_pacman_pos == ghost.pos:
                            self.game_status = 'lose'
                            break
                        # 2. Cả hai di chuyển đến cùng một vị trí
                        elif new_pacman_pos == new_ghost_pos:
                            self.game_status = 'lose'
                            break
                
                # --- KIỂM TRA XOAY MÊ CUNG (sau mỗi 30 bước) ---
                if self.game_status != 'lose':
                    step_count = self.game_state.step_count
                    # Chỉ xoay khi step_count vừa đạt bội số của 30 và chưa xoay lần này
                    if step_count > 0 and step_count % 30 == 0 and (not hasattr(self, '_last_rotation_step') or self._last_rotation_step != step_count):
                        try:
                            # Lưu kích thước cũ để tính toán xoay
                            old_rows = self.grid.rows
                            old_cols = self.grid.cols
                            
                            # Xoay mê cung
                            self.grid.rotate_90_degrees_right()
                            
                            # Xoay tất cả các vị trí entities
                            self.game_state = self.rules._rotate_entity_positions(self.game_state, old_rows, old_cols)
                            
                            # Cập nhật màn hình sau khi xoay
                            self._update_screen_after_rotation()
                            
                            # Đánh dấu đã xoay ở step này
                            self._last_rotation_step = step_count
                            
                        except Exception as e:
                            print(f"Error rotating maze at step {step_count}: {e}")
                
                # --- XỬ LÝ TELEPORTATION SELECTION ---
                if hasattr(self.agent, 'teleport_choice') and self.agent.teleport_choice is not None:
                    if self.game_state.pacman.waiting_for_teleport:
                        self.game_state = self.rules.handle_teleport_selection(self.game_state, self.agent.teleport_choice)
                        self.agent.teleport_choice = None  # Reset choice
                
                # --- APPLY ACTION: Dùng Rules để tính GameState tiếp theo ---
                if action and self.game_status != 'lose':
                    old_cols = self.grid.cols
                    old_rows = self.grid.rows
                    
                    self.game_state = self.rules.get_successor(self.game_state, action)
                    
                    # Kiểm tra xem mê cung có bị xoay không
                    if self.grid.cols != old_cols or self.grid.rows != old_rows:
                        self._update_screen_after_rotation()
                            
                    # --- KIỂM TRA VA CHẠM SAU KHI DI CHUYỂN (BACKUP CHECK) ---
                    # LUÔN LUÔN kiểm tra va chạm - bất cứ khi nào chạm Ghost đều thua
                    if self.game_status != 'lose':
                        pacman_pos = self.game_state.pacman.pos
                        for ghost in self.game_state.ghosts:
                            if ghost.pos == pacman_pos:
                                self.game_status = 'lose'
                                break

                    # Nếu chưa thua, kiểm tra thắng
                    if self.game_status != 'lose':
                        food_left = len(self.game_state.food_left) 
                        at_exit = self.game_state.pacman.pos == self.grid.exitgate_pos
                        
                        if food_left <= 0 and at_exit: # Điều kiện thắng 
                            self.game_status = 'win'

            # --- VẼ ---
            self.renderer.draw_all(self.game_state)

            if self.game_status == 'win': 
                self.renderer.draw_win_screen(self.game_state.step_count) 
            elif self.game_status == 'lose':
                self.renderer.draw_lose_screen()

            pygame.display.flip() 
            
            # Điều chỉnh tốc độ dựa trên loại agent
            if hasattr(self.agent, 'heuristic_type'):  # AutoAgent
                self.clock.tick(10) # 10 FPS = 0.1 giây cho mỗi bước)
            else:  # ManualAgent
                self.clock.tick(60)  # 60 FPS cho manual 
        
        # Trả về 'quit' nếu vòng lặp bị phá vỡ
        return 'quit'