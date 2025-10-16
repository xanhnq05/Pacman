import pygame
import sys
import os

# --- HẰNG SỐ ---
# Kích thước của mỗi ô trong mê cung (ví dụ: 20x20 pixels)
CELL_SIZE = 30
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
# Tốc độ hoạt ảnh (số frame trước khi chuyển ảnh)
ANIMATION_SPEED = 10 

class PacmanGame:
    def __init__(self, layout_file):
        """
        Hàm khởi tạo game.
        """
        pygame.init()
        self.layout = self.load_layout(layout_file) # mảng này chứa từng dòng của file layout.txt
        self.rows = len(self.layout)    # số hàng bằng số phần tử = 18
        self.cols = len(self.layout[0]) # số cột bằng chiều dài của hàng đầu tiên = 36
        
        # Tính toán kích thước cửa sổ dựa trên layout
        self.screen_width = self.cols * CELL_SIZE
        self.screen_height = (self.rows + 2) * CELL_SIZE
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pacman - user mode")

        # Tìm vị trí ban đầu của Pacman và các đối tượng khác
        self.find_objects()

        # Thay thế các biến chớp tắt bằng các biến cho hiệu ứng FADE
        self.food_alpha = 255      # Giá trị alpha hiện tại của thức ăn (bắt đầu ở 255 - rõ nhất)
        self.fade_speed = -3       # Tốc độ thay đổi alpha (âm để bắt đầu mờ đi)
        self.min_alpha = 150        # Độ mờ tối thiểu (để không bị biến mất hoàn toàn)
        self.max_alpha = 255       # Độ mờ tối đa (rõ nét)
        self.food_color_rgb = (255, 255, 0) # Màu vàng

        # --- HOẠT ẢNH PACMAN ---
        self.pacman_idle_images = []
        self.load_pacman_idle_images()
        self.current_idle_frame = 0
        self.animation_counter = 0 # Đếm số frame đã trôi qua

        # Lưu trữ hướng di chuyển hiện tại (góc xoay)
        # 0: Phải, 90: Lên, 180: Trái, 270: Xuống
        self.pacman_direction = 0 
        self.step = 0
        self.font = pygame.font.Font(None, 32)
        
        # -----------------------------------
        self.clock = pygame.time.Clock() # Dùng để kiểm soát FPS

    def load_layout(self, layout_file):
        """
        Đọc file layout và chuyển thành một mảng 2D.
        """
        with open(layout_file, 'r') as f:
            return [line.strip() for line in f]

    def find_objects(self):
        """
        Tìm và lưu trữ vị trí của Pacman và thức ăn.
        """
        self.pacman_pos = None
        self.food_pos = []
        self.magical_pie = []
        for r, row in enumerate(self.layout):
            for c, char in enumerate(row):
                if char == 'P':
                    # Vị trí Pacman
                    self.pacman_pos = [r, c]
                elif char == '.':
                    self.food_pos.append([r, c])
                elif char == '0':
                    self.magical_pie.append([r,c])

    def load_pacman_idle_images(self):
        """
        Tải các hình ảnh Pacman cho hiệu ứng idle.
        """
        # Tạo danh sách các tên file ảnh
        image_files = [
            '1.png', 
            '2.png', 
            '3.png', 
            '4.png'
        ]

        base_dir = os.path.dirname(__file__)
        folder_name = "assets\player_images"

        
        for file_name in image_files:
            # os.path.join đảm bảo đường dẫn đúng trên mọi hệ điều hành
            path = os.path.join(base_dir, folder_name, file_name)
            try:
                image = pygame.image.load(path).convert_alpha() # .convert_alpha() tốt cho ảnh có trong suốt
                # Thay đổi kích thước ảnh để phù hợp với CELL_SIZE
                image = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
                self.pacman_idle_images.append(image)
            except pygame.error as e:
                print(f"Không thể tải ảnh {file_name}: {e}")
                sys.exit()
        
        if not self.pacman_idle_images:
            print("Không có ảnh Pacman nào được tải. Đảm bảo các file ảnh tồn tại.")
            sys.exit()

    def draw_maze(self):
       
        """
        Vẽ các thành phần tĩnh của mê cung: tường và thức ăn.
        """
        offset_y = 2 * CELL_SIZE 
        for r, row in enumerate(self.layout):
            for c, char in enumerate(row):
                if char == '%': # Tường
                    # Vẽ hình chữ nhật với tọa độ Y đã cộng offset
                    pygame.draw.rect(self.screen, BLUE, (c * CELL_SIZE, r * CELL_SIZE + offset_y, CELL_SIZE, CELL_SIZE))

    def draw_food(self):
        """
        Vẽ thức ăn.
        """
        offset_y = 2 * CELL_SIZE
        for food in self.food_pos:
            r, c = food
            # Vẽ một hình tròn nhỏ màu trắng cho thức ăn
            center_x = c * CELL_SIZE + CELL_SIZE // 2
            center_y = r * CELL_SIZE + CELL_SIZE // 2 + offset_y
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y), CELL_SIZE // 6)

    def draw_magical_pie(self):
        offset_y = 2 * CELL_SIZE
        for pie in self.magical_pie:
            r, c = pie
            # Vẽ chiếc bánh ma thuật

            # Tạo một bề mặt tạm thời có kích thước bằng một ô
            # cờ pygame.SRCALPHA cho phép bề mặt này có độ trong suốt
            temp_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            
            # Tạo màu sắc cho hình tròn bao gồm cả giá trị alpha hiện tại
            current_color = (*self.food_color_rgb, self.food_alpha) # Ví dụ: (255, 255, 0, 150)
            
            # Vẽ hình tròn LÊN BỀ MẶT TẠM THỜI
            # Tâm của hình tròn sẽ là tâm của bề mặt tạm thời
            circle_center_on_surface = (CELL_SIZE // 2, CELL_SIZE // 2)
            pygame.draw.circle(temp_surface, current_color, circle_center_on_surface, CELL_SIZE // 3)
            
            # Tính toán vị trí góc trên bên trái để "dán" bề mặt tạm thời lên màn hình chính
            blit_pos_x = c * CELL_SIZE
            blit_pos_y = r * CELL_SIZE + offset_y
            
            # "Dán" bề mặt tạm thời lên màn hình chính
            self.screen.blit(temp_surface, (blit_pos_x, blit_pos_y))
            
    def draw_pacman(self):
        """
        Vẽ Pacman sử dụng ảnh hoạt hình idle và xoay theo hướng.
        """
        offset_y = 2 * CELL_SIZE
        if self.pacman_pos and self.pacman_idle_images:
            
            # Lấy ảnh hiện tại từ hoạt ảnh idle
            # self.current_idle_frame được cập nhật trong update_animation()
            image_to_rotate = self.pacman_idle_images[self.current_idle_frame]
            
            # Xoay ảnh theo hướng hiện tại
            rotated_image = pygame.transform.rotate(image_to_rotate, self.pacman_direction)

            # Tính toán vị trí để vẽ ảnh (góc trên bên trái của ô)
            draw_x = self.pacman_pos[1] * CELL_SIZE
            draw_y = self.pacman_pos[0] * CELL_SIZE + offset_y
            
            # Tạo một hình chữ nhật bao quanh ảnh đã xoay, đặt tâm của nó vào tâm ô
            rect = rotated_image.get_rect(center=(draw_x + CELL_SIZE // 2, draw_y + CELL_SIZE // 2))

            # Vẽ ảnh lên màn hình, sử dụng vị trí của rect
            self.screen.blit(rotated_image, rect)

    def move_pacman(self, dr, dc):
        """
        Di chuyển Pacman, kiểm tra va chạm tường, và **cập nhật hướng xoay**.
        """

        # **Cập nhật hướng xoay DỰA TRÊN dr và dc**
        if dr == -1 and dc == 0:    # Lên
            self.pacman_direction = 90
        elif dr == 1 and dc == 0:   # Xuống
            self.pacman_direction = 270
        elif dr == 0 and dc == -1:  # Trái
            self.pacman_direction = 180
        elif dr == 0 and dc == 1:   # Phải
            self.pacman_direction = 0

        if self.pacman_pos:
            new_r = self.pacman_pos[0] + dr
            new_c = self.pacman_pos[1] + dc
            
            # Kiểm tra xem vị trí mới có hợp lệ không (không phải tường)
            if 0 <= new_r < self.rows and 0 <= new_c < self.cols and self.layout[new_r][new_c] != '%':
                self.pacman_pos = [new_r, new_c]

                # cập nhật số bước đi
                self.step += 1                
                # Kiểm tra ăn thức ăn
                if self.pacman_pos in self.food_pos:
                    self.food_pos.remove(self.pacman_pos)
                if self.pacman_pos in self.magical_pie:
                    self.magical_pie.remove(self.pacman_pos)

    def draw_step(self):
        """
        Vẽ số bước đi của Pacman lên khu vực phía trên màn hình.
        """
        # Tạo bề mặt text (render)
        text_surface = self.font.render(f"Step: {self.step}", True, WHITE)
        
        # Lấy kích thước của text
        text_rect = text_surface.get_rect()
        
        # Đặt text ở góc trên bên trái của khu vực thông tin (ô 0, 0)
        # Tọa độ Y nhỏ (CELL_SIZE // 2) đảm bảo nó nằm trong khu vực 2 ô trống đầu tiên
        text_rect.topleft = (CELL_SIZE // 2, CELL_SIZE // 2)
        
        # Vẽ text lên màn hình
        self.screen.blit(text_surface, text_rect)

    def update_animation(self):
        """
        Cập nhật khung hình hoạt ảnh của Pacman.
        """
        self.animation_counter += 1
        if self.animation_counter >= ANIMATION_SPEED:
            self.current_idle_frame = (self.current_idle_frame + 1) % len(self.pacman_idle_images)
            self.animation_counter = 0

    def update_animation_magical_pie(self):
        # 1. Cập nhật giá trị alpha
        self.food_alpha += self.fade_speed

        # 2. Đảo ngược hướng fade khi chạm đến giới hạn min hoặc max
        if self.food_alpha <= self.min_alpha or self.food_alpha >= self.max_alpha:
            # Đảm bảo alpha không vượt quá giới hạn
            self.food_alpha = max(self.min_alpha, min(self.food_alpha, self.max_alpha))
            # Đảo chiều tốc độ
            self.fade_speed = -self.fade_speed

    def run(self):
        """
        Vòng lặp chính của game.
        """
        running = True
        while running:
            # Xử lý sự kiện (nhấn phím, thoát game)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Xử lý sự kiện nhấn phím cho chế độ chơi thủ công
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.move_pacman(-1, 0) # Lên
                    elif event.key == pygame.K_DOWN:
                        self.move_pacman(1, 0)  # Xuống
                    elif event.key == pygame.K_LEFT:
                        self.move_pacman(0, -1) # Trái
                    elif event.key == pygame.K_RIGHT:
                        self.move_pacman(0, 1)  # Phải
            
            # --- Logic cho hiệu ứng FADE ---
            self.update_animation_magical_pie()

            # ---- PHẦN VẼ ----
            # 1. Xóa màn hình bằng màu đen
            self.screen.fill(BLACK)
            
            # 2. Vẽ các đối tượng
            self.draw_maze()
            self.draw_food()
            self.draw_pacman()
            self.draw_magical_pie()
            
            # Vẽ điểm số
            self.draw_step()

            # Cập nhật hoạt ảnh của Pacman
            self.update_animation()

            # Giới hạn tốc độ khung hình (ví dụ: 30 FPS)
            self.clock.tick(60) 

            # Cập nhật màn hình để hiển thị những gì đã vẽ
            pygame.display.flip()
        
        # Thoát game
        pygame.quit()
        sys.exit()

# --- CHẠY GAME ---
if __name__ == "__main__":
    game = PacmanGame("layout.txt")
    game.run()