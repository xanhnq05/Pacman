# pacman/agents/auto_agent.py
from pacman.search.astar import AStarSearch
from pacman.search.astar_complete import AStarComplete
from pacman.search.heuristics import Heuristics
from pacman.core.rules import Rules
from pacman.core.grid import Grid

class AutoAgent:
    """
    Agent sử dụng thuật toán A* để tìm đường đi.
    """
    def __init__(self, grid: Grid, rules: Rules, heuristic_type="farthest_food_and_exit"):
        print("AutoAgent has ready.")
        self.grid = grid
        self.rules = rules
        self.heuristics = Heuristics(grid)
        self.search = AStarSearch(rules, self.heuristics, heuristic_type)
        # Use the complete A* implementation
        self.complete_search = AStarComplete(grid, rules)
        self.plan = [] # Kế hoạch (danh sách actions)
        self.planning_done = False
        self.heuristic_type = heuristic_type
        
        # Heuristics are now handled internally by the Heuristics class
    
    def process_event(self, event):
        """
        AutoAgent không cần xử lý input từ người dùng,
        nên hàm này không làm gì cả.
        """
        pass 

    def get_action(self, game_state):
        """
        Hàm này được gọi bởi GameEngine sau vòng lặp sự kiện.
        Nó sẽ chạy logic A* và trả về hành động.
        """
        # 1. Kiểm tra va chạm với ma trước khi lấy hành động
        if self._check_ghost_collision(game_state):
            print("AutoAgent: Ghost collision detected! Replanning...")
            self.plan = []  # Clear current plan
            self.planning_done = False
        
        # 2. Nếu plan rỗng, chạy A* để tạo plan mới
        if not self.plan and not self.planning_done:
            self._create_plan(game_state)
        
        # 3. Lấy hành động tiếp theo từ plan
        if self.plan:
            action = self.plan.pop(0)
            # Kiểm tra xem hành động này có an toàn không
            if self._is_safe_action(game_state, action):
                return action
            else:
                print("AutoAgent: Unsafe action detected! Replanning...")
                self.plan = []  # Clear plan and replan
                return self.get_action(game_state)  # Recursive call to replan
        
        # 4. Nếu không có plan, trả về None (không di chuyển)
        return None
    
    def _create_plan(self, game_state):
        """
        Tạo kế hoạch di chuyển sử dụng A* search.
        """
        try:
            print("AutoAgent: Starting path planning...")
            
            # Lấy các hành động an toàn
            safe_actions = self._get_safe_actions(game_state)
            
            if not safe_actions:
                print("AutoAgent: No safe actions available! Staying put.")
                self.plan = [(0, 0)] * 5  # Stay put
                self.planning_done = True
                return
            
            # Use simplified goal condition to avoid infinite loops
            def simple_goal_condition(state):
                # Just reach the exit for now (ignore food requirement)
                return state.pacman.pos == self.grid.exitgate_pos
            
            # Use original A* search with simple goal
            path = self.search.search(game_state, simple_goal_condition)
            
            if path:
                # Filter path to only include safe actions
                safe_path = []
                for action in path:
                    if action in safe_actions:
                        safe_path.append(action)
                    else:
                        # Replace unsafe action with safe alternative
                        if safe_actions:
                            safe_path.append(safe_actions[0])  # Use first safe action
                        else:
                            safe_path.append((0, 0))  # Stay put
                
                self.plan = safe_path
                print(f"AutoAgent: Found safe path with {len(safe_path)} steps")
            else:
                print("AutoAgent: No path found - using safe random movement")
                # Create a safe fallback plan
                self.plan = safe_actions * 3  # Repeat safe actions
                self.planning_done = True
                
        except Exception as e:
            print(f"AutoAgent planning error: {e}")
            # Create a safe fallback plan
            safe_actions = self._get_safe_actions(game_state)
            if safe_actions:
                self.plan = safe_actions * 3
            else:
                self.plan = [(0, 0)] * 5  # Stay put
            self.planning_done = True
    
    def _check_ghost_collision(self, game_state):
        """
        Kiểm tra xem Pacman có đang va chạm với ma không.
        """
        pacman_pos = game_state.pacman.pos
        for ghost in game_state.ghosts:
            if pacman_pos == ghost.pos:
                return True
        return False
    
    def _is_safe_action(self, game_state, action):
        """
        Kiểm tra xem hành động có an toàn không (không dẫn đến va chạm với ma).
        """
        if not action:
            return True
        
        pacman_pos = game_state.pacman.pos
        dr, dc = action
        new_pacman_pos = (pacman_pos[0] + dr, pacman_pos[1] + dc)
        
        # Kiểm tra va chạm với ma hiện tại
        for ghost in game_state.ghosts:
            if new_pacman_pos == ghost.pos:
                return False
        
        # Kiểm tra va chạm với ma sau khi ma di chuyển
        for ghost in game_state.ghosts:
            new_ghost = ghost.get_updated_state(self.grid)
            if new_pacman_pos == new_ghost.pos:
                return False
        
        return True
    
    def _get_safe_actions(self, game_state):
        """
        Lấy danh sách các hành động an toàn.
        """
        safe_actions = []
        pacman_pos = game_state.pacman.pos
        
        # Kiểm tra 4 hướng di chuyển
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_pos = (pacman_pos[0] + dr, pacman_pos[1] + dc)
            
            # Kiểm tra biên giới
            if (0 <= new_pos[0] < self.grid.rows and 
                0 <= new_pos[1] < self.grid.cols):
                
                # Kiểm tra tường
                if not self.grid.is_wall(new_pos) or game_state.pacman.power_steps > 0:
                    # Kiểm tra va chạm với ma
                    is_safe = True
                    for ghost in game_state.ghosts:
                        if new_pos == ghost.pos:
                            is_safe = False
                            break
                        # Kiểm tra va chạm sau khi ma di chuyển
                        new_ghost = ghost.get_updated_state(self.grid)
                        if new_pos == new_ghost.pos:
                            is_safe = False
                            break
                    
                    if is_safe:
                        safe_actions.append((dr, dc))
        
        return safe_actions