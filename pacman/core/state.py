# pacman/core/state.py
from pacman.core.entities import Pacman, Ghost # <-- IMPORT MỚI

class GameState:
    """
    Định nghĩa trạng thái trò chơi bất biến (immutable) và hashable.
    """
    def __init__(self, pacman, ghosts, food_left, pies_left, step_count):
        # THAY ĐỔI: Lưu trữ đối tượng, không phải tuple
        self.pacman = pacman           # Đối tượng Pacman
        self.ghosts = ghosts           # Tuple của các đối tượng Ghost
        
        self.food_left = food_left     # frozenset
        self.pies_left = pies_left     # frozenset
        self.step_count = step_count
        
        # Tạo cache cho hash
        self._hash = hash((self.pacman, self.ghosts, self.food_left, self.pies_left))

    def __eq__(self, other):
        """So sánh hai trạng thái có bằng nhau không."""
        if not isinstance(other, GameState):
            return NotImplemented
        return self.pacman == other.pacman and \
               self.ghosts == other.ghosts and \
               self.food_left == other.food_left and \
               self.pies_left == other.pies_left

    def __hash__(self):
        """Tính toán giá trị hash cho trạng thái."""
        return self._hash

    @staticmethod
    def get_initial_state(grid):
        """Tạo trạng thái khởi tạo từ Grid tĩnh."""
        
        # Tạo đối tượng Pacman ban đầu
        initial_pacman = Pacman(grid.initial_pacman_pos)
        
        # Tạo các đối tượng Ghost ban đầu (TODO: lấy từ grid)
        initial_ghosts = []
        for pos, color, direction in grid.initial_ghosts_info:
             initial_ghosts.append(Ghost(pos, color, direction))
        
        return GameState(
            pacman=initial_pacman,
            ghosts=tuple(initial_ghosts), # Chuyển sang tuple để hashable
            food_left=frozenset(grid.initial_food_pos),
            pies_left=frozenset(grid.initial_magical_pie),
            step_count=0
        )