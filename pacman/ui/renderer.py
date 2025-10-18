import pygame
import os
import sys

CELL_SIZE = 30
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ANIMATION_SPEED = 10 

class Renderer:
    def __init__(self, screen, grid):
        self.screen = screen
        self.grid = grid # Tham chiếu đến đối tượng Grid
        self.screen_width = grid.cols * CELL_SIZE
        self.screen_height = (grid.rows + 2) * CELL_SIZE
        
        # Tải ảnh và Font
        self.pacman_idle_images = self._load_pacman_idle_images()
        self.exitgate_image = self._load_exitgate_image()
        # TODO: self.ghost_images = self._load_ghost_images()
        self.font = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_large = pygame.font.Font(None, 74)

        # Biến hoạt ảnh và hiệu ứng
        self.current_idle_frame = 0
        self.animation_counter = 0 
        self.food_alpha = 255      # Giá trị alpha hiện tại của bánh ma thuật
        self.fade_speed = -3 
        self.min_alpha = 150
        self.max_alpha = 255
        self.food_color_rgb = YELLOW
        
    def _get_asset_path(self, folder_name, file_name):
        """
        Xây dựng đường dẫn tuyệt đối đến tệp tài nguyên (asset).
        Cấu trúc: Renderer (ui/renderer.py) -> pacman -> assets/folder_name/file_name
        """
        # os.path.dirname(__file__) là thư mục 'ui'
        # os.path.dirname(os.path.dirname(__file__)) là thư mục 'pacman'
        # Sau đó ta nối đến thư mục 'assets' ngang hàng với 'pacman'
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, "assets", folder_name, file_name)

    def _load_pacman_idle_images(self):
        """
        Tải các hình ảnh Pacman cho hiệu ứng idle và scale chúng.
        """
        image_files = ['1.png', '2.png', '3.png', '4.png']
        images = []
        folder_name = "player_images"
        
        for file_name in image_files:
            path = self._get_asset_path(folder_name, file_name)
            try:
                # Tải ảnh và chuyển đổi định dạng có hỗ trợ trong suốt
                image = pygame.image.load(path).convert_alpha() 
                # Thay đổi kích thước ảnh để phù hợp với CELL_SIZE
                image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
                images.append(image)
            except pygame.error as e:
                print(f"Lỗi: Không thể tải ảnh Pacman '{file_name}'. Đảm bảo đường dẫn chính xác: {path}")
                sys.exit()
        
        if not images:
            print("Lỗi: Không có ảnh Pacman nào được tải.")
            sys.exit()
            
        return images

    def _load_exitgate_image(self):
        """
        Tải hình ảnh cổng thoát.
        """
        file_name = "exitgate.png"
        folder_name = "player_images"
        path = self._get_asset_path(folder_name, file_name)
        
        try:
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
            return image
        except pygame.error as e:
            print(f"Lỗi: Không thể tải ảnh Cổng thoát '{file_name}'. Đảm bảo đường dẫn chính xác: {path}")
            sys.exit()
        
    # TODO: Bổ sung _load_ghost_images() tương tự

    def update_animation(self):
        """Cập nhật khung hình hoạt ảnh của Pacman."""
        self.animation_counter += 1
        if self.animation_counter >= ANIMATION_SPEED:
            self.current_idle_frame = (self.current_idle_frame + 1) % len(self.pacman_idle_images)
            self.animation_counter = 0

    def update_animation_magical_pie(self):
        """Cập nhật hiệu ứng chớp tắt (fade) cho bánh ma thuật."""
        self.food_alpha += self.fade_speed
        if self.food_alpha <= self.min_alpha or self.food_alpha >= self.max_alpha:
            self.food_alpha = max(self.min_alpha, min(self.food_alpha, self.max_alpha))
            self.fade_speed = -self.fade_speed

    def draw_all(self, game_state, pacman_direction):
        """Hàm tổng hợp để vẽ mọi thứ dựa trên GameState hiện tại."""
        
        self.screen.fill(BLACK)
        offset_y = 2 * CELL_SIZE
        
        # --- 1. Vẽ Tường (Maze) ---
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                if self.grid.layout_list[r][c] == '%': # Tường
                    pygame.draw.rect(self.screen, BLUE, (c * CELL_SIZE, r * CELL_SIZE + offset_y, CELL_SIZE, CELL_SIZE))
        
        # --- 2. Vẽ Thức ăn (Food) ---
        for r, c in game_state.food_left:
            center_x = c * CELL_SIZE + CELL_SIZE // 2
            center_y = r * CELL_SIZE + CELL_SIZE // 2 + offset_y
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y), CELL_SIZE // 6)

        # --- 3. Vẽ Bánh ma thuật (Magical Pies) với hiệu ứng fade ---
        for r, c in game_state.pies_left:
            temp_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            current_color = (*self.food_color_rgb, self.food_alpha)
            circle_center_on_surface = (CELL_SIZE // 2, CELL_SIZE // 2)
            pygame.draw.circle(temp_surface, current_color, circle_center_on_surface, CELL_SIZE // 3)
            
            blit_pos_x = c * CELL_SIZE
            blit_pos_y = r * CELL_SIZE + offset_y
            self.screen.blit(temp_surface, (blit_pos_x, blit_pos_y))
            
        # --- 4. Vẽ Cổng thoát (Exit Gate) ---
        # Giả định cổng thoát mở khi thức ăn còn lại <= 6, như trong oldmain.py
        if len(game_state.food_left) <= 6 and self.grid.exitgate_pos and self.exitgate_image:
            r, c = self.grid.exitgate_pos
            draw_x = c * CELL_SIZE
            draw_y = r * CELL_SIZE + offset_y
            self.screen.blit(self.exitgate_image, (draw_x, draw_y))
            
        # --- 5. Vẽ Pacman với hoạt ảnh và xoay ---
        if self.pacman_idle_images:
            r, c = game_state.pacman_pos
            image_to_rotate = self.pacman_idle_images[self.current_idle_frame]
            rotated_image = pygame.transform.rotate(image_to_rotate, pacman_direction)
            
            draw_x = c * CELL_SIZE
            draw_y = r * CELL_SIZE + offset_y
            rect = rotated_image.get_rect(center=(draw_x + CELL_SIZE // 2, draw_y + CELL_SIZE // 2))
            self.screen.blit(rotated_image, rect)
        
        # --- 6. Vẽ thông tin (HUD) ---
        self.draw_step(game_state.step_count)
        self.draw_score(len(game_state.food_left))
        
        # Cập nhật màn hình
        # pygame.display.flip()

    def draw_step(self, step_count):
        """Vẽ số bước đi."""
        text_surface = self.font.render(f"Step: {step_count}", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (CELL_SIZE // 2, CELL_SIZE // 2)
        self.screen.blit(text_surface, text_rect)

    def draw_score(self, food_remain):
        """Vẽ số thức ăn còn lại."""
        text_surface = self.font.render(f"Food remain: {food_remain} ", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topright = (self.screen_width - CELL_SIZE // 2, CELL_SIZE // 2)
        self.screen.blit(text_surface, text_rect)

    def draw_win_screen(self, step_count):
        """
        Vẽ màn hình thông báo chiến thắng.
        """
        # Tạo bề mặt mờ (Overlay)
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200)) # Màu đen, độ trong suốt 200
        self.screen.blit(s, (0, 0))

        win_text = self.font_large.render(f"YOU WIN!", True, YELLOW)
        step_text = self.font_medium.render(f"Total Steps: {step_count}", True, WHITE)
        restart_text = self.font_small.render("Press 'R' to restart", True, WHITE)
        menu_text = self.font_small.render("Press 'ESC' for Main Menu", True, WHITE)
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        self.screen.blit(win_text, win_text.get_rect(center=(center_x, center_y - 70)))
        self.screen.blit(step_text, step_text.get_rect(center=(center_x, center_y + 0)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(center_x, center_y + 70)))
        self.screen.blit(menu_text, menu_text.get_rect(center=(center_x, center_y + 110)))