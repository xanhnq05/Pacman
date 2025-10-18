# pacman/ui/renderer.py
import pygame
import os
import sys

# Khai báo HẰNG SỐ cần thiết
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
        
        # Tải ảnh
        self.pacman_idle_images = self._load_pacman_idle_images()
        self.exitgate_image = self._load_exitgate_image()
        self.font = pygame.font.Font(None, 32)
        
        # Biến hoạt ảnh
        self.current_idle_frame = 0
        self.animation_counter = 0 
        self.food_alpha = 255
        self.fade_speed = -3 
        self.min_alpha = 150
        self.max_alpha = 255
        self.food_color_rgb = YELLOW
        
    def _load_pacman_idle_images(self):
        # Logic tải ảnh Pacman (giữ nguyên từ PacmanGame.load_pacman_idle_images)
        # Cần điều chỉnh đường dẫn file cho phù hợp với cấu trúc
        # Ví dụ: base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "player_images")
        # (Để đơn giản hóa, ta bỏ qua phần code tải ảnh tại đây và giả định nó hoạt động)
        print("Renderer: Đang tải ảnh Pacman...")
        return [pygame.Surface((CELL_SIZE, CELL_SIZE))] * 4 # Placeholder

    def _load_exitgate_image(self):
        # Logic tải ảnh ExitGate
        print("Renderer: Đang tải ảnh Cổng thoát...")
        return pygame.Surface((CELL_SIZE, CELL_SIZE)) # Placeholder

    def update_animation(self):
        # Logic cập nhật hoạt ảnh Pacman (giữ nguyên từ PacmanGame.update_animation)
        self.animation_counter += 1
        if self.animation_counter >= ANIMATION_SPEED:
            self.current_idle_frame = (self.current_idle_frame + 1) % len(self.pacman_idle_images)
            self.animation_counter = 0

    def update_animation_magical_pie(self):
        # Logic cập nhật hoạt ảnh bánh ma thuật (giữ nguyên)
        self.food_alpha += self.fade_speed
        if self.food_alpha <= self.min_alpha or self.food_alpha >= self.max_alpha:
            self.food_alpha = max(self.min_alpha, min(self.food_alpha, self.max_alpha))
            self.fade_speed = -self.fade_speed

    def draw_all(self, game_state, pacman_direction):
        """Hàm tổng hợp để vẽ mọi thứ dựa trên GameState hiện tại."""
        
        self.screen.fill(BLACK)
        offset_y = 2 * CELL_SIZE
        
        # Vẽ Tường
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                if self.grid.layout_list[r][c] == '%':
                    pygame.draw.rect(self.screen, BLUE, (c * CELL_SIZE, r * CELL_SIZE + offset_y, CELL_SIZE, CELL_SIZE))
        
        # Vẽ Thức ăn (food_left từ GameState)
        for r, c in game_state.food_left:
            center_x = c * CELL_SIZE + CELL_SIZE // 2
            center_y = r * CELL_SIZE + CELL_SIZE // 2 + offset_y
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y), CELL_SIZE // 6)

        # Vẽ Bánh ma thuật (pies_left từ GameState)
        for r, c in game_state.pies_left:
            temp_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            current_color = (*self.food_color_rgb, self.food_alpha)
            circle_center_on_surface = (CELL_SIZE // 2, CELL_SIZE // 2)
            pygame.draw.circle(temp_surface, current_color, circle_center_on_surface, CELL_SIZE // 3)
            blit_pos_x = c * CELL_SIZE
            blit_pos_y = r * CELL_SIZE + offset_y
            self.screen.blit(temp_surface, (blit_pos_x, blit_pos_y))
            
        # Vẽ Cổng thoát (chỉ khi đủ điều kiện)
        if len(game_state.food_left) <= 6 and self.grid.exitgate_pos:
            r, c = self.grid.exitgate_pos
            draw_x = c * CELL_SIZE
            draw_y = r * CELL_SIZE + offset_y
            self.screen.blit(self.exitgate_image, (draw_x, draw_y))
            
        # Vẽ Pacman
        r, c = game_state.pacman_pos
        image_to_rotate = self.pacman_idle_images[self.current_idle_frame]
        rotated_image = pygame.transform.rotate(image_to_rotate, pacman_direction)
        draw_x = c * CELL_SIZE
        draw_y = r * CELL_SIZE + offset_y
        rect = rotated_image.get_rect(center=(draw_x + CELL_SIZE // 2, draw_y + CELL_SIZE // 2))
        self.screen.blit(rotated_image, rect)
        
        # Vẽ thông tin (Step, Food remain)
        self.draw_step(game_state.step_count)
        self.draw_score(len(game_state.food_left))
        
        # Cập nhật màn hình
        pygame.display.flip()

    # Giữ nguyên draw_step và draw_score, nhưng nhận dữ liệu từ tham số
    def draw_step(self, step_count):
        text_surface = self.font.render(f"Step: {step_count}", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (CELL_SIZE // 2, CELL_SIZE // 2)
        self.screen.blit(text_surface, text_rect)

    def draw_score(self, food_remain):
        text_surface = self.font.render(f"Food remain: {food_remain} ", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topright = (self.screen_width - CELL_SIZE // 2, CELL_SIZE // 2)
        self.screen.blit(text_surface, text_rect)