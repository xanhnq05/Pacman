# pacman/core/rules.py
from pacman.core.state import GameState
from pacman.core.entities import Pacman, Ghost

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
        current_pacman = current_state.pacman
        (r, c) = current_pacman.pos
        food_left = set(current_state.food_left)
        pies_left = set(current_state.pies_left)
        power_steps = current_pacman.power_steps
        step_count = current_state.step_count
        
        # 2. Xoay mê cung được xử lý riêng trong game loop
        
        # 3. Tính toán vị trí mới
        dr, dc = action
        new_r, new_c = r + dr, c + dc
        new_pos = (new_r, new_c)

        # 3.5. Kiểm tra biên giới mê cung (ngăn Pacman ra ngoài mê cung)
        if not self._is_within_bounds(new_pos):
            return current_state  # Không cho phép di chuyển ra ngoài mê cung

        # 4. Kiểm tra teleport
        if self.grid.is_teleport_corner(new_pos):
            # Nếu Pacman đang chờ teleport, không cho phép di chuyển
            if current_pacman.waiting_for_teleport:
                return current_state
            
            # Nếu Pacman đến góc teleport lần đầu, đặt trạng thái chờ
            teleport_options = self.grid.get_teleport_destinations(new_pos)
            if teleport_options:
                print(f"Pacman reached teleport corner {new_pos}. Press 1-4 to select destination:")
                for i, option in enumerate(teleport_options, 1):
                    print(f"  {i}: {option}")
                
                # Tạo Pacman mới với trạng thái chờ teleport
                new_pacman = Pacman(new_pos, current_pacman.direction, power_steps, waiting_for_teleport=True)
                return GameState(
                    pacman=new_pacman,
                    ghosts=current_state.ghosts,
                    food_left=current_state.food_left,
                    pies_left=current_state.pies_left,
                    step_count=step_count + 1
                )

        # 5. Kiểm tra va chạm và luật di chuyển
        can_move = False
        is_wall = self.grid.is_wall(new_pos)

        if not is_wall:
            can_move = True
            if power_steps > 0: power_steps -= 1
        elif is_wall and power_steps > 0:
            can_move = True
            self.grid.eat_wall(new_pos)
            power_steps -= 1
        else:
            can_move = False
            
        if not can_move:
            return current_state 

        # 6. Nếu di chuyển thành công, cập nhật trạng thái
        step_count += 1
        
        if new_pos in food_left:
            food_left.remove(new_pos)
        if new_pos in pies_left:
            pies_left.remove(new_pos)
            power_steps = 5 # Kích hoạt Power Mode

        # Tính hướng xoay mới cho Pacman
        new_direction = current_pacman.direction
        if dr == -1: new_direction = 90
        elif dr == 1: new_direction = 270
        elif dc == -1: new_direction = 180
        elif dc == 1: new_direction = 0

        # TẠO ĐỐI TƯỢNG PACMAN MỚI
        new_pacman = Pacman(new_pos, new_direction, power_steps)

        # 7. Cập nhật trạng thái Ghosts
        new_ghosts = []
        for ghost in current_state.ghosts:
            # Ghost di chuyển bình thường
            new_ghosts.append(ghost.get_updated_state(self.grid))

        # 8. Tạo và trả về GameState mới
        return GameState(
            pacman=new_pacman,
            ghosts=tuple(new_ghosts),
            food_left=frozenset(food_left),
            pies_left=frozenset(pies_left),
            step_count=step_count
        )
    
    def _rotate_entity_positions(self, state, old_rows, old_cols):
        """
        Xoay tất cả các vị trí entities sau khi xoay mê cung.
        Công thức xoay 90 độ sang phải: (r, c) -> (c, old_rows - 1 - r)
        """
        # Xoay vị trí Pacman
        old_pacman_pos = state.pacman.pos
        new_pacman_r = old_pacman_pos[1]  # c -> r
        new_pacman_c = old_rows - 1 - old_pacman_pos[0]  # old_rows - 1 - r -> c
        new_pacman_pos = (new_pacman_r, new_pacman_c)
        
        
        # Tạo Pacman mới với vị trí đã xoay
        new_pacman = Pacman(new_pacman_pos, state.pacman.direction, state.pacman.power_steps)
        
        # Xoay vị trí các Ghosts
        new_ghosts = []
        for ghost in state.ghosts:
            old_ghost_pos = ghost.pos
            new_ghost_r = old_ghost_pos[1]  # c -> r
            new_ghost_c = old_rows - 1 - old_ghost_pos[0]  # old_rows - 1 - r -> c
            new_ghost_pos = (new_ghost_r, new_ghost_c)
            
            # Tạo Ghost mới với vị trí đã xoay (giữ nguyên color và direction)
            new_ghost = Ghost(new_ghost_pos, ghost.color, ghost.direction)
            new_ghosts.append(new_ghost)
        
        # Xoay vị trí thức ăn
        new_food_left = set()
        for food_pos in state.food_left:
            old_food_r, old_food_c = food_pos
            new_food_r = old_food_c  # c -> r
            new_food_c = old_rows - 1 - old_food_r  # old_rows - 1 - r -> c
            new_food_pos = (new_food_r, new_food_c)
            new_food_left.add(new_food_pos)
        
        # Xoay vị trí bánh ma thuật
        new_pies_left = set()
        for pie_pos in state.pies_left:
            old_pie_r, old_pie_c = pie_pos
            new_pie_r = old_pie_c  # c -> r
            new_pie_c = old_rows - 1 - old_pie_r  # old_rows - 1 - r -> c
            new_pie_pos = (new_pie_r, new_pie_c)
            new_pies_left.add(new_pie_pos)
        
        
        return GameState(new_pacman, tuple(new_ghosts), frozenset(new_food_left), frozenset(new_pies_left), state.step_count)
    
    def _is_within_bounds(self, pos):
        """
        Kiểm tra xem vị trí có nằm trong biên giới mê cung không.
        Ngăn Pacman di chuyển ra ngoài mê cung.
        """
        r, c = pos
        return 0 <= r < self.grid.rows and 0 <= c < self.grid.cols
    
    def handle_teleport_selection(self, current_state, teleport_choice):
        """
        Xử lý việc chọn teleportation thủ công.
        teleport_choice: 1, 2, 3, hoặc 4 (tương ứng với các góc teleport)
        """
        if not current_state.pacman.waiting_for_teleport:
            return current_state
        
        # Lấy danh sách các góc teleport có thể đến
        teleport_options = self.grid.get_teleport_destinations(current_state.pacman.pos)
        
        # Kiểm tra lựa chọn hợp lệ
        if 1 <= teleport_choice <= len(teleport_options):
            destination = teleport_options[teleport_choice - 1]
            
            # Tạo Pacman mới với vị trí đích và tắt trạng thái chờ
            new_pacman = Pacman(destination, current_state.pacman.direction, 
                              current_state.pacman.power_steps, waiting_for_teleport=False)
            
            print(f"Pacman teleported from {current_state.pacman.pos} to {destination}")
            
            # Cập nhật step count và kiểm tra thức ăn/pie tại vị trí mới
            new_food_left = set(current_state.food_left)
            new_pies_left = set(current_state.pies_left)
            new_power_steps = current_state.pacman.power_steps
            
            if destination in new_food_left:
                new_food_left.remove(destination)
            if destination in new_pies_left:
                new_pies_left.remove(destination)
                new_power_steps = 5  # Kích hoạt Power Mode
            
            # Tạo Pacman cuối cùng với power_steps đã cập nhật
            final_pacman = Pacman(destination, current_state.pacman.direction, 
                                new_power_steps, waiting_for_teleport=False)
            
            return GameState(
                pacman=final_pacman,
                ghosts=current_state.ghosts,
                food_left=frozenset(new_food_left),
                pies_left=frozenset(new_pies_left),
                step_count=current_state.step_count + 1
            )
        
        return current_state
    
    def get_successor_for_astar(self, current_state, action):
        """
        Tính toán trạng thái tiếp theo dành riêng cho A* search.
        Tự động xử lý teleport để tối ưu đường đi.
        """
        
        # 1. Lấy thông tin trạng thái hiện tại
        current_pacman = current_state.pacman
        (r, c) = current_pacman.pos
        food_left = set(current_state.food_left)
        pies_left = set(current_state.pies_left)
        power_steps = current_pacman.power_steps
        step_count = current_state.step_count
        
        # 2. Tính toán vị trí mới
        dr, dc = action
        new_r, new_c = r + dr, c + dc
        new_pos = (new_r, new_c)

        # 3. Kiểm tra biên giới mê cung
        if not self._is_within_bounds(new_pos):
            return current_state

        # 4. Xử lý teleport tự động cho A*
        if self.grid.is_teleport_corner(new_pos):
            teleport_options = self.grid.get_teleport_destinations(new_pos)
            if teleport_options:
                # Tự động chọn teleport tốt nhất dựa trên heuristic
                best_destination = self._choose_best_teleport_for_astar(
                    new_pos, teleport_options, current_state
                )
                new_pos = best_destination
                
                # Kiểm tra thức ăn tại vị trí teleport mới
                if new_pos in food_left:
                    food_left.remove(new_pos)
                if new_pos in pies_left:
                    pies_left.remove(new_pos)
                    power_steps = 5  # Kích hoạt Power Mode

        # 5. Kiểm tra va chạm và luật di chuyển
        can_move = False
        is_wall = self.grid.is_wall(new_pos)

        if not is_wall:
            can_move = True
            if power_steps > 0: power_steps -= 1
        elif is_wall and power_steps > 0:
            can_move = True
            self.grid.eat_wall(new_pos)
            power_steps -= 1
        else:
            can_move = False
            
        if not can_move:
            return current_state 

        # 6. Nếu di chuyển thành công, cập nhật trạng thái
        step_count += 1
        
        if new_pos in food_left:
            food_left.remove(new_pos)
        if new_pos in pies_left:
            pies_left.remove(new_pos)
            power_steps = 5 # Kích hoạt Power Mode

        # Tính hướng xoay mới cho Pacman
        new_direction = current_pacman.direction
        if dr == -1: new_direction = 90
        elif dr == 1: new_direction = 270
        elif dc == -1: new_direction = 180
        elif dc == 1: new_direction = 0

        # TẠO ĐỐI TƯỢNG PACMAN MỚI
        new_pacman = Pacman(new_pos, new_direction, power_steps)

        # 7. Cập nhật trạng thái Ghosts
        new_ghosts = []
        for ghost in current_state.ghosts:
            # Ghost di chuyển bình thường
            new_ghosts.append(ghost.get_updated_state(self.grid))

        # 8. Tạo và trả về GameState mới
        return GameState(
            pacman=new_pacman,
            ghosts=tuple(new_ghosts),
            food_left=frozenset(food_left),
            pies_left=frozenset(pies_left),
            step_count=step_count
        )
    
    def _choose_best_teleport_for_astar(self, current_pos, teleport_options, current_state):
        """
        Chọn teleport tốt nhất cho A* dựa trên khoảng cách đến thức ăn gần nhất.
        """
        pacman_pos = current_pos
        
        if not current_state.food_left:
            # Không còn thức ăn, chọn teleport gần exit gate nhất
            if self.grid.exitgate_pos:
                min_dist = float('inf')
                best_dest = teleport_options[0]
                for dest in teleport_options:
                    dist = self._bfs_maze_distance(dest, self.grid.exitgate_pos)
                    if dist < min_dist:
                        min_dist = dist
                        best_dest = dest
                return best_dest
            return teleport_options[0]
        
        # Còn thức ăn, chọn teleport gần thức ăn gần nhất
        min_total_dist = float('inf')
        best_dest = teleport_options[0]
        
        for dest in teleport_options:
            # Tính khoảng cách từ teleport dest đến thức ăn gần nhất
            min_food_dist = float('inf')
            for food_pos in current_state.food_left:
                dist = self._bfs_maze_distance(dest, food_pos)
                min_food_dist = min(min_food_dist, dist)
            
            # Tính tổng khoảng cách (từ pacman đến teleport + từ teleport đến thức ăn)
            total_dist = 1 + min_food_dist  # Cost teleport là 1
            
            if total_dist < min_total_dist:
                min_total_dist = total_dist
                best_dest = dest
        
        return best_dest
    
    def _bfs_maze_distance(self, start, goal):
        """
        Tính khoảng cách thực tế trong mê cung bằng BFS.
        """
        from collections import deque
        
        if start == goal:
            return 0
            
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            pos, dist = queue.popleft()
            
            if pos == goal:
                return dist
            
            # Check all 4 directions
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_pos = (pos[0] + dr, pos[1] + dc)
                
                if (new_pos not in visited and 
                    0 <= new_pos[0] < self.grid.rows and 
                    0 <= new_pos[1] < self.grid.cols and
                    not self.grid.is_wall(new_pos)):
                    visited.add(new_pos)
                    queue.append((new_pos, dist + 1))
        
        return float('inf')  # No path found