# pacman/core/entities.py
''' class ghost:
    def __init__(self, x, y, color, direction, leftLimit, rightLimit):
        self.x = x
        self.y = y
        self.direction = direction #rotate follow the direction degrees 90 or -90
        self.leftLimit = leftLimit
        self.rightLimit = rightLimit
        self.speed = 1
        self.radius = 10
        self.color = color

    def load_graphic(self):
        path = f'assets/ghost_image/{self.color}.png' #path to the images
        self.image = pygame.image.load(path).convert_alpha() # load the image following the color value
        self.image = pygame.transform.scale(self.image, (self.radius, self.radius)) # scale the image to the radius
        self.image = pygame.transform.rotate(self.image, self.direction) #load graphic that rotating follow the direction
        self.rect = self.image.get_rect() # init the rect
        self.rect.center = (self.x, self.y)# set x,y to the rect that has been initialized

    def update(self, maze):
        new_x = self.x + self.speed * self.direction
        # Nếu phía trước là tường → quay đầu lại
        if maze.is_wall(new_x, self.y):
            self.direction *= -1
        else:
        # Không phải tường → di chuyển bình thường
            self.x = new_x
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
'''
class Ghost:
    """
    Lớp trạng thái BẤT BIẾN (immutable) cho Ghost.
    """
    def __init__(self, pos, color, direction_vector):
        """
        pos: (r, c)
        color: 'red', 'blue', v.v.
        direction_vector: (dr, dc). Vì ma chỉ di chuyển ngang,
                          nó sẽ là (0, 1) [Phải] hoặc (0, -1) [Trái].
        """
        self.pos = pos
        self.color = color
        self.direction = direction_vector

    def __eq__(self, other):
        """Dùng để so sánh trạng thái Ghost"""
        return isinstance(other, Ghost) and \
               self.pos == other.pos and \
               self.direction == other.direction

    def __hash__(self):
        """Dùng cho 'closed set' của A*"""
        return hash((self.pos, self.direction, self.color))

    def get_updated_state(self, grid):
        """
        Đây là logic 'update' từ class ghost cũ của bạn,
        nhưng thay vì 'self.x = ...', nó trả về một
        đối tượng Ghost MỚI.
        """
        dr, dc = self.direction # (0, 1) hoặc (0, -1)
        
        # Tính vị trí mới (chỉ di chuyển ngang)
        new_r, new_c = self.pos[0], self.pos[1] + dc
        
        # Kiểm tra va chạm tường (Sử dụng logic của bạn)
        # (Lưu ý: hàm is_wall của grid nhận (r, c) tuple)
        if grid.is_wall((new_r, new_c)):
            # Chạm tường, quay đầu
            new_direction = (dr, -dc)
            # Trả về trạng thái MỚI, vị trí CŨ (vì không di chuyển được)
            return Ghost(self.pos, self.color, new_direction)
        else:
            # Không chạm, trả về trạng thái MỚI, vị trí MỚI
            return Ghost((new_r, new_c), self.color, self.direction)

class Pacman:
    """
    Lớp trạng thái BẤT BIẾN (immutable) cho Pacman.
    Dùng để lưu trữ trong GameState.
    """
    def __init__(self, pos, direction=0, power_steps=0, waiting_for_teleport=False):
        self.pos = pos # (r, c)
        self.direction = direction # 0: Phải, 90: Lên, 180: Trái, 270: Xuống
        self.power_steps = power_steps
        self.waiting_for_teleport = waiting_for_teleport  # True nếu đang chờ chọn teleport

    def __eq__(self, other):
        """Dùng để so sánh các trạng thái trong A*"""
        return isinstance(other, Pacman) and \
               self.pos == other.pos and \
               self.power_steps == other.power_steps and \
               self.waiting_for_teleport == other.waiting_for_teleport

    def __hash__(self):
        """Dùng cho 'closed set' của A*"""
        return hash((self.pos, self.power_steps, self.waiting_for_teleport))