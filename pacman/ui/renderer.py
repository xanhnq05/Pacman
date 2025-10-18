import pygame
import os
import sys

CELL_SIZE = 20
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
# Màu nền mới - xanh đậm cho không gian
DARK_BLUE = (10, 20, 40)
# Màu tường fallback nếu không có texture
WALL_BLUE = (30, 60, 120)
ANIMATION_SPEED = 10 

class Renderer:
    def __init__(self, screen, grid):
        self.screen = screen
        self.grid = grid # Tham chiếu đến đối tượng Grid
        self._update_screen_dimensions()
        
        # Tải ảnh và Font
        self.pacman_idle_images = self._load_pacman_idle_images()
        self.exitgate_image = self._load_exitgate_image()
        self.ghost_images = self._load_ghost_images(["red", "pink", "blue", "orange"])
        self.wall_texture = self._load_wall_texture()

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
        
        # Teleportation effects
        self.teleport_alpha = 255
        self.teleport_fade_speed = -5
        self.teleport_min_alpha = 100
        self.teleport_max_alpha = 255
        self.teleport_color = (0, 255, 255)  # Cyan color for teleportation
    
    def _update_screen_dimensions(self):
        """
        Cập nhật kích thước màn hình dựa trên grid hiện tại.
        """
        self.screen_width = self.grid.cols * CELL_SIZE
        self.screen_height = (self.grid.rows + 2) * CELL_SIZE
        
    def update_grid(self, new_grid):
        """
        Cập nhật grid mới và kích thước màn hình.
        """
        self.grid = new_grid
        self._update_screen_dimensions()
        
    def update_screen(self, new_screen):
        """
        Cập nhật screen mới sau khi xoay mê cung.
        """
        self.screen = new_screen
        
    def _load_ghost_images(self, colors):
        """
        Tải các hình ảnh Ghost.
        """
        images = {}
        folder_name = "ghost_images"
        for color in colors:
            file_name = f"{color}.png"
            path = self._get_asset_path(folder_name, file_name)
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
                images[color] = image
            except pygame.error as e:
                print(f"Lỗi: Không thể tải ảnh Ghost '{file_name}'.")
                # Không thoát, có thể tiếp tục với màu mặc định
        return images

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
    
    def _load_wall_texture(self):
        """
        Tải texture tường và scale cho phù hợp với CELL_SIZE.
        """
        file_name = "wall128x128.png"
        folder_name = "player_images"
        path = self._get_asset_path(folder_name, file_name)
        
        try:
            texture = pygame.image.load(path).convert()
            # Scale texture để phù hợp với kích thước cell
            texture = pygame.transform.scale(texture, (CELL_SIZE, CELL_SIZE))
            return texture
        except pygame.error as e:
            print(f"Lỗi: Không thể tải texture tường '{file_name}'. Đảm bảo đường dẫn chính xác: {path}")
            # Trả về None nếu không tải được, sẽ fallback về màu xanh
            return None
        
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
    
    def update_teleport_animation(self):
        """Cập nhật hiệu ứng chớp tắt cho teleportation corners."""
        self.teleport_alpha += self.teleport_fade_speed
        if self.teleport_alpha <= self.teleport_min_alpha or self.teleport_alpha >= self.teleport_max_alpha:
            self.teleport_alpha = max(self.teleport_min_alpha, min(self.teleport_alpha, self.teleport_max_alpha))
            self.teleport_fade_speed = -self.teleport_fade_speed

    def draw_all(self, game_state):
        """Hàm tổng hợp để vẽ mọi thứ dựa trên GameState hiện tại."""
        try:
            # Đảm bảo screen được cập nhật đúng kích thước
            if hasattr(self, 'screen') and self.screen is not None:
                # Sử dụng màu nền mới thay vì đen
                self.screen.fill(DARK_BLUE)
            else:
                print("Error: Screen is None!")
                return
                
            offset_y = 2 * CELL_SIZE
            
            # --- 1. Vẽ Tường (Maze) với texture ---
            wall_count = 0
            for r in range(self.grid.rows):
                for c in range(self.grid.cols):
                    if self.grid.layout_list[r][c] == '%': # Tường
                        draw_x = c * CELL_SIZE
                        draw_y = r * CELL_SIZE + offset_y
                        
                        # Sử dụng texture nếu có, fallback về màu nếu không
                        if self.wall_texture:
                            self.screen.blit(self.wall_texture, (draw_x, draw_y))
                        else:
                            pygame.draw.rect(self.screen, WALL_BLUE, (draw_x, draw_y, CELL_SIZE, CELL_SIZE))
                        wall_count += 1
            
            
            # --- 2. Vẽ Thức ăn (Food) với màu sáng hơn ---
            for r, c in game_state.food_left:
                center_x = c * CELL_SIZE + CELL_SIZE // 2
                center_y = r * CELL_SIZE + CELL_SIZE // 2 + offset_y
                # Sử dụng màu vàng sáng cho thức ăn
                pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), CELL_SIZE // 6)

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
            if len(game_state.food_left) <= 0 and self.grid.exitgate_pos and self.exitgate_image:
                r, c = self.grid.exitgate_pos
                draw_x = c * CELL_SIZE
                draw_y = r * CELL_SIZE + offset_y
                self.screen.blit(self.exitgate_image, (draw_x, draw_y))
                
            # --- 5. Vẽ Pacman với hoạt ảnh và xoay ---
            if self.pacman_idle_images:
                # Lấy Pacman object từ state
                pacman = game_state.pacman 
                r, c = pacman.pos
                pacman_direction = pacman.direction # <-- LẤY HƯỚNG TỪ STATE
                
                image_to_rotate = self.pacman_idle_images[self.current_idle_frame]
                rotated_image = pygame.transform.rotate(image_to_rotate, pacman_direction)
                
                draw_x = c * CELL_SIZE
                draw_y = r * CELL_SIZE + offset_y
                rect = rotated_image.get_rect(center=(draw_x + CELL_SIZE // 2, draw_y + CELL_SIZE // 2))
                self.screen.blit(rotated_image, rect)
            
            # --- 6. Vẽ Ghosts ---
            for ghost in game_state.ghosts:
                r, c = ghost.pos
                color = ghost.color
                if color in self.ghost_images:
                    image = self.ghost_images[color]
                    draw_x = c * CELL_SIZE
                    draw_y = r * CELL_SIZE + offset_y
                    rect = image.get_rect(center=(draw_x + CELL_SIZE // 2, draw_y + CELL_SIZE // 2))
                    self.screen.blit(image, rect)

            # --- 7. Vẽ Teleportation Corners ---
            self.draw_teleport_corners(offset_y)
            
            # --- 7.5. Vẽ Teleportation Selection UI ---
            if game_state.pacman.waiting_for_teleport:
                self.draw_teleport_selection_ui(game_state)
            
            # --- 8. Vẽ thông tin (HUD) ---
            self.draw_step(game_state.step_count)
            self.draw_score(len(game_state.food_left))
            
        except Exception as e:
            print(f"Error in draw_all: {e}")
            import traceback
            traceback.print_exc()
            # Không thoát game, chỉ in lỗi

    def draw_step(self, step_count):
        """Vẽ số bước đi."""
        # Thêm background cho text để dễ đọc hơn
        text_surface = self.font.render(f"Step: {step_count}", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (CELL_SIZE // 2, CELL_SIZE // 2)
        
        # Vẽ background đen mờ cho text
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), bg_rect)
        self.screen.blit(text_surface, text_rect)

    def draw_score(self, food_remain):
        """Vẽ số thức ăn còn lại."""
        text_surface = self.font.render(f"Food remain: {food_remain} ", True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topright = (self.screen_width - CELL_SIZE // 2, CELL_SIZE // 2)
        
        # Vẽ background đen mờ cho text
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), bg_rect)
        self.screen.blit(text_surface, text_rect)
    
    def draw_teleport_corners(self, offset_y):
        """Vẽ các góc teleportation với hiệu ứng chớp tắt."""
        for r, c in self.grid.teleport_corners:
            # Tạo surface với alpha để có hiệu ứng fade
            temp_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            current_color = (*self.teleport_color, self.teleport_alpha)
            
            # Vẽ hình tròn với hiệu ứng fade
            center = (CELL_SIZE // 2, CELL_SIZE // 2)
            pygame.draw.circle(temp_surface, current_color, center, CELL_SIZE // 3)
            
            # Vẽ viền để làm nổi bật
            pygame.draw.circle(temp_surface, (255, 255, 255, 200), center, CELL_SIZE // 3, 2)
            
            # Vẽ chữ "T" để chỉ teleport
            font_small = pygame.font.Font(None, 16)
            text_surface = font_small.render("T", True, (255, 255, 255, 255))
            text_rect = text_surface.get_rect(center=center)
            temp_surface.blit(text_surface, text_rect)
            
            # Blit lên màn hình
            draw_x = c * CELL_SIZE
            draw_y = r * CELL_SIZE + offset_y
            self.screen.blit(temp_surface, (draw_x, draw_y))
    
    def draw_teleport_selection_ui(self, game_state):
        """Vẽ UI để chọn teleportation destination."""
        # Tạo overlay mờ
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Lấy danh sách các góc teleport có thể đến
        teleport_options = self.grid.get_teleport_destinations(game_state.pacman.pos)
        
        # Vẽ hướng dẫn
        instruction_text = self.font_medium.render("Select teleport destination:", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Vẽ các lựa chọn
        for i, option in enumerate(teleport_options, 1):
            r, c = option
            # Tính toán vị trí trên màn hình
            screen_x = c * CELL_SIZE + CELL_SIZE // 2
            screen_y = r * CELL_SIZE + CELL_SIZE // 2 + 2 * CELL_SIZE
            
            # Vẽ số lựa chọn
            choice_text = self.font_medium.render(f"{i}", True, YELLOW)
            choice_rect = choice_text.get_rect(center=(screen_x, screen_y - 30))
            self.screen.blit(choice_text, choice_rect)
            
            # Vẽ vòng tròn highlight
            pygame.draw.circle(self.screen, YELLOW, (screen_x, screen_y), CELL_SIZE // 2, 3)
            
            # Vẽ tọa độ
            # coord_text = self.font_small.render(f"({r},{c})", True, WHITE)
            # coord_rect = coord_text.get_rect(center=(screen_x, screen_y + 20))
            # self.screen.blit(coord_text, coord_rect)
        
        # Vẽ hướng dẫn phím
        help_text = self.font_small.render("Press 1-4 to select destination", True, WHITE)
        help_rect = help_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
        self.screen.blit(help_text, help_rect)

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
        
        self.screen.blit(win_text, win_text.get_rect(center=(center_x, center_y - 50)))
        self.screen.blit(step_text, step_text.get_rect(center=(center_x, center_y - 10)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(center_x, center_y + 40)))
        self.screen.blit(menu_text, menu_text.get_rect(center=(center_x, center_y + 80)))

    def draw_lose_screen(self):
        """
        Vẽ màn hình thông báo Thua Cuộc (Game Over).
        """
        # Tạo bề mặt mờ (Overlay)
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 220)) # Màu đen, mờ hơn win
        self.screen.blit(s, (0, 0))

        game_over_text = self.font_large.render(f"GAME OVER", True, (255, 0, 0)) # Màu đỏ
        restart_text = self.font_small.render("Press 'R' to restart", True, WHITE)
        menu_text = self.font_small.render("Press 'ESC' for Main Menu", True, WHITE)
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        self.screen.blit(game_over_text, game_over_text.get_rect(center=(center_x, center_y - 50)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(center_x, center_y + 40)))
        self.screen.blit(menu_text, menu_text.get_rect(center=(center_x, center_y + 80)))