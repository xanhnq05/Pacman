# pacman/core/state.py

class GameState:
    """
    Định nghĩa trạng thái trò chơi bất biến (immutable) và hashable.
    Đây là node mà thuật toán A* sẽ làm việc.
    """
    def __init__(self, pacman_pos, food_left, pies_left, power_mode_steps, step_count, ghosts_state):
        # Vị trí Pacman: (r, c)
        self.pacman_pos = pacman_pos 
        
        # Thức ăn còn lại: Sử dụng frozenset để có thể hashable (không thay đổi được)
        self.food_left = food_left
        
        # Bánh ma thuật còn lại: frozenset của (r, c)
        self.pies_left = pies_left 
        
        # Số bước còn lại có thể ăn tường
        self.power_mode_steps = power_mode_steps 
        
        # Số bước đã đi (để kiểm tra khi nào thì xoay mê cung)
        self.step_count = step_count
        
        # Trạng thái của các bóng ma (ví dụ: tuple của (r, c, direction))
        self.ghosts_state = ghosts_state

    # ------------------
    # Yêu cầu quan trọng cho A*: Bất biến và Hashable
    # ------------------
    
    def __eq__(self, other):
        """So sánh hai trạng thái có bằng nhau không."""
        if not isinstance(other, GameState):
            return NotImplemented
        return (self.pacman_pos == other.pacman_pos and
                self.food_left == other.food_left and
                self.pies_left == other.pies_left and
                self.power_mode_steps == other.power_mode_steps and
                # Không cần so sánh step_count và ghosts_state nếu bạn chỉ muốn 
                # kiểm tra trạng thái game lõi. Nhưng để chính xác cho A*, 
                # nên so sánh tất cả các thuộc tính động.
                self.step_count == other.step_count and
                self.ghosts_state == other.ghosts_state)
    
    def __hash__(self):
        """Tính toán giá trị hash cho trạng thái."""
        return hash((self.pacman_pos, 
                     self.food_left, 
                     self.pies_left,
                     self.power_mode_steps,
                     self.step_count,
                     self.ghosts_state))

    @staticmethod
    def get_initial_state(grid, initial_ghosts):
        """Tạo trạng thái khởi tạo từ Grid tĩnh."""
        return GameState(
            pacman_pos=grid.initial_pacman_pos,
            food_left=frozenset(grid.initial_food_pos),
            pies_left=frozenset(grid.initial_magical_pie),
            power_mode_steps=0,
            step_count=0,
            ghosts_state=initial_ghosts # Giả sử là tuple/frozenset
        )