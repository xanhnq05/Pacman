# pacman/core/rules.py
from pacman.core.state import GameState

class Rules:
    """
    Lớp này chứa logic chuyển đổi trạng thái (Transition Model).
    Nó nhận một trạng thái và một hành động, sau đó trả về trạng thái mới.
    """
    def __init__(self, grid):
        """
        Lưu trữ tham chiếu đến grid, vì grid có thể bị thay đổi (khi ăn tường).
        """
        self.grid = grid

    def get_successor(self, current_state, action):
        """
        Tính toán trạng thái tiếp theo (successor) dựa trên hành động.
        action là một tuple (dr, dc), ví dụ: (-1, 0) là LÊN.
        """
        
        # 1. Lấy thông tin trạng thái hiện tại
        (r, c) = current_state.pacman_pos
        food_left = set(current_state.food_left) # Chuyển sang set để có thể thay đổi
        pies_left = set(current_state.pies_left) # Chuyển sang set để có thể thay đổi
        power_steps = current_state.power_mode_steps
        step_count = current_state.step_count
        
        # 2. Tính toán vị trí mới
        dr, dc = action
        new_r, new_c = r + dr, c + dc
        new_pos = (new_r, new_c)

        # 3. Kiểm tra va chạm và luật di chuyển
        
        can_move = False
        is_wall = self.grid.is_wall(new_pos)

        # Trường hợp 1: Không phải tường
        if not is_wall:
            can_move = True
            # Nếu đang trong Power Mode, giảm số bước đi
            if power_steps > 0:
                power_steps -= 1
        
        # Trường hợp 2: Là tường, VÀ đang trong Power Mode (ăn tường)
        elif is_wall and power_steps > 0:
            can_move = True
            self.grid.eat_wall(new_pos) # Yêu cầu grid "ăn" bức tường này
            power_steps -= 1 # Tiêu thụ 1 bước Power Mode
            print(f"Wall eaten at {new_pos}! Steps left: {power_steps}")

        # Trường hợp 3: Là tường, KHÔNG có Power Mode
        else:
            can_move = False
            
        # 4. Nếu không thể di chuyển (đâm vào tường)
        if not can_move:
            # Trả về trạng thái y hệt hiện tại (không di chuyển, không tốn bước)
            return current_state 

        # 5. Nếu di chuyển thành công, cập nhật trạng thái mới
        step_count += 1
        
        # Ăn thức ăn
        if new_pos in food_left:
            food_left.remove(new_pos)
            
        # Ăn bánh ma thuật
        if new_pos in pies_left:
            pies_left.remove(new_pos)
            power_steps = 5 # Kích hoạt Power Mode trong 5 BƯỚC
            print("Magical Pie eaten! Power Mode activated for 5 steps.")

        # Tạo và trả về GameState mới
        return GameState(
            pacman_pos=new_pos,
            food_left=frozenset(food_left), # Chuyển lại frozenset
            pies_left=frozenset(pies_left), # Chuyển lại frozenset
            power_mode_steps=power_steps,
            step_count=step_count,
            ghosts_state=current_state.ghosts_state # (Tạm thời giữ nguyên ghost)
        )