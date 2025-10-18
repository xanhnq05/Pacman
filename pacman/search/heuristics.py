# pacman/search/heuristics.py
"""
Heuristic functions for A* search in Pacman.
Includes h1 (BFS), h2 (MST), FarthestFoodAndExit, and distance caching.
"""

from pacman.core.state import GameState
from pacman.core.grid import Grid
from typing import Dict, Tuple, Set, Optional
import heapq
from collections import deque


class Heuristics:
    """
    Collection of heuristic functions for A* search.
    """
    
    def __init__(self, grid: Grid):
        self.grid = grid
        self.distance_cache: Dict[Tuple[Tuple[int, int], Tuple[int, int]], int] = {}
        # Global cache for BFS distances (from heuristic.py)
        self._distance_cache: Dict[Tuple[Tuple[int, int], Tuple[int, int]], int] = {}
        
    def maze_distance_heuristic(self, state: GameState) -> int:
        """
        Custom maze distance heuristic using BFS-based pathfinding.
        Considers avoiding ghosts and using magical pies for wall eating.
        This is admissible and consistent since it uses actual shortest paths in the maze.
        """
        pacman_pos = state.pacman.pos
        
        if not state.food_left:
            # No food left, go to exit gate
            if self.grid.exitgate_pos:
                return self._bfs_maze_distance(pacman_pos, self.grid.exitgate_pos)
            return 0
        
        # Find nearest food using actual maze distance
        min_food_dist = float('inf')
        for food_pos in state.food_left:
            dist = self._bfs_maze_distance(pacman_pos, food_pos)
            min_food_dist = min(min_food_dist, dist)
        
        # Add penalty for being near ghosts (to encourage avoiding them)
        ghost_penalty = self._calculate_ghost_penalty(state)
        
        # Consider magical pie usage for wall eating
        pie_bonus = self._calculate_pie_bonus(state)
        
        base_cost = min_food_dist if min_food_dist != float('inf') else 0
        return base_cost + ghost_penalty - pie_bonus
    
    def teleport_aware_heuristic(self, state: GameState) -> int:
        """
        Enhanced heuristic that considers teleportation capabilities.
        Uses maze distance but optimizes for teleport corners when beneficial.
        """
        pacman_pos = state.pacman.pos
        
        if not state.food_left:
            # No food left, go to exit gate
            if self.grid.exitgate_pos:
                return self._teleport_aware_distance(pacman_pos, self.grid.exitgate_pos)
            return 0
        
        # Find nearest food considering teleports
        min_food_dist = float('inf')
        for food_pos in state.food_left:
            dist = self._teleport_aware_distance(pacman_pos, food_pos)
            min_food_dist = min(min_food_dist, dist)
        
        return min_food_dist if min_food_dist != float('inf') else 0
    
    def tsp_maze_heuristic(self, state: GameState) -> int:
        """
        Traveling Salesman Problem-based heuristic using maze distances.
        Estimates the minimum cost to collect all remaining food using MST.
        This is admissible and consistent.
        """
        pacman_pos = state.pacman.pos
        
        if not state.food_left:
            # No food left, go to exit gate
            if self.grid.exitgate_pos:
                return self._bfs_maze_distance(pacman_pos, self.grid.exitgate_pos)
            return 0
        
        # Create list of all positions (pacman + food)
        positions = [pacman_pos] + list(state.food_left)
        
        # Calculate MST cost for all food positions
        mst_cost = self._calculate_mst_cost(positions)
        
        # Add distance to nearest food (since we need to start collecting)
        min_food_dist = min(
            self._bfs_maze_distance(pacman_pos, food_pos) 
            for food_pos in state.food_left
        )
        
        return mst_cost + min_food_dist
    
    def teleport_aware_heuristic(self, state: GameState) -> int:
        """
        Teleport-aware heuristic - xem xét khả năng teleport.
        Sử dụng khoảng cách maze nhưng ưu tiên các góc teleport.
        """
        pacman_pos = state.pacman.pos
        
        if not state.food_left:
            # No food left, go to exit gate
            if self.grid.exitgate_pos:
                return self._teleport_aware_distance(pacman_pos, self.grid.exitgate_pos)
            return 0
        
        # Find nearest food considering teleports
        min_food_dist = float('inf')
        for food_pos in state.food_left:
            dist = self._teleport_aware_distance(pacman_pos, food_pos)
            min_food_dist = min(min_food_dist, dist)
        
        return min_food_dist if min_food_dist != float('inf') else 0
    
    def _teleport_aware_distance(self, start: Tuple[int, int], goal: Tuple[int, int]) -> int:
        """
        Tính khoảng cách có xem xét teleport.
        """
        # Nếu start hoặc goal là góc teleport, có thể teleport
        if self.grid.is_teleport_corner(start) or self.grid.is_teleport_corner(goal):
            # Kiểm tra xem có thể teleport đến gần goal hơn không
            min_dist = self._bfs_maze_distance(start, goal)
            
            # Thử teleport từ start
            if self.grid.is_teleport_corner(start):
                for teleport_dest in self.grid.get_teleport_destinations(start):
                    dist = self._bfs_maze_distance(teleport_dest, goal)
                    min_dist = min(min_dist, dist)
            
            # Thử teleport đến goal
            if self.grid.is_teleport_corner(goal):
                for teleport_dest in self.grid.get_teleport_destinations(goal):
                    dist = self._bfs_maze_distance(start, teleport_dest)
                    min_dist = min(min_dist, dist)
            
            return min_dist
        else:
            # Không có teleport, dùng BFS thông thường
            return self._bfs_maze_distance(start, goal)
    
    def bfs_distance(self, state: GameState) -> int:
        """
        BFS-based heuristic (h1).
        Uses BFS to find actual shortest path to nearest food.
        """
        pacman_pos = state.pacman.pos
        
        if not state.food_left:
            # No food left, use BFS to exit gate
            if self.grid.exitgate_pos:
                return self._bfs_maze_distance(pacman_pos, self.grid.exitgate_pos)
            return 0
        
        # Find nearest food using BFS
        min_food_dist = float('inf')
        for food_pos in state.food_left:
            dist = self._bfs_maze_distance(pacman_pos, food_pos)
            min_food_dist = min(min_food_dist, dist)
        
        return min_food_dist if min_food_dist != float('inf') else 0
    
    def mst_heuristic(self, state: GameState) -> int:
        """
        MST-based heuristic (h2).
        Uses Minimum Spanning Tree to estimate cost of collecting all food.
        """
        if not state.food_left:
            return 0
            
        # Create list of all positions (pacman + food)
        positions = [state.pacman.pos] + list(state.food_left)
        
        # Calculate MST cost
        return self._calculate_mst_cost(positions)
    
    def _manhattan_dist(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _bfs_maze_distance(self, start: Tuple[int, int], goal: Tuple[int, int]) -> int:
        """
        Calculate actual maze distance using BFS.
        Caches results for efficiency.
        """
        cache_key = (start, goal)
        if cache_key in self.distance_cache:
            return self.distance_cache[cache_key]
        
        # BFS to find shortest path
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            pos, dist = queue.popleft()
            
            if pos == goal:
                self.distance_cache[cache_key] = dist
                return dist
            
            # Check all 4 directions
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_pos = (pos[0] + dr, pos[1] + dc)
                
                if (new_pos not in visited and 
                    not self.grid.is_wall(new_pos)):
                    visited.add(new_pos)
                    queue.append((new_pos, dist + 1))
        
        # No path found
        self.distance_cache[cache_key] = float('inf')
        return float('inf')
    
    def _calculate_mst_cost(self, positions: list) -> int:
        """
        Calculate Minimum Spanning Tree cost for given positions.
        Uses Prim's algorithm.
        """
        if len(positions) <= 1:
            return 0
        
        # Calculate all pairwise distances
        distances = {}
        for i, pos1 in enumerate(positions):
            for j, pos2 in enumerate(positions[i+1:], i+1):
                dist = self._bfs_maze_distance(pos1, pos2)
                distances[(i, j)] = dist
                distances[(j, i)] = dist
        
        # Prim's algorithm
        mst_cost = 0
        visited = {0}  # Start with first position
        edges = []
        
        # Initialize heap with edges from first position
        for j in range(1, len(positions)):
            heapq.heappush(edges, (distances.get((0, j), float('inf')), 0, j))
        
        while len(visited) < len(positions):
            if not edges:
                break
                
            cost, i, j = heapq.heappop(edges)
            
            if j not in visited:
                visited.add(j)
                mst_cost += cost
                
                # Add new edges from j
                for k in range(len(positions)):
                    if k not in visited:
                        heapq.heappush(edges, (distances.get((j, k), float('inf')), j, k))
        
        return mst_cost
    
    def _calculate_ghost_penalty(self, state: GameState) -> int:
        """
        Tính penalty khi Pacman ở gần ma để khuyến khích né ma.
        """
        pacman_pos = state.pacman.pos
        penalty = 0
        
        for ghost in state.ghosts:
            # Tính khoảng cách Manhattan đến ma (nhanh hơn BFS cho mục đích này)
            manhattan_dist = abs(pacman_pos[0] - ghost.pos[0]) + abs(pacman_pos[1] - ghost.pos[1])
            
            # Nếu ở quá gần ma (trong vòng 3 ô), thêm penalty
            if manhattan_dist <= 3:
                penalty += (4 - manhattan_dist) * 2  # Penalty giảm dần theo khoảng cách
        
        return penalty
    
    def _calculate_pie_bonus(self, state: GameState) -> int:
        """
        Tính bonus khi có magical pie để ăn tường.
        """
        pacman_pos = state.pacman.pos
        bonus = 0
        
        # Nếu đang có power (từ magical pie), giảm cost
        if state.pacman.power_steps > 0:
            bonus += state.pacman.power_steps
        
        # Nếu có magical pie gần đó, thêm bonus nhỏ
        for pie_pos in state.pies_left:
            dist = self._bfs_maze_distance(pacman_pos, pie_pos)
            if dist <= 5:  # Nếu pie ở gần (trong vòng 5 bước)
                bonus += max(0, 6 - dist)  # Bonus giảm dần theo khoảng cách
        
        return bonus
    
    def farthest_food_and_exit_heuristic(self, state: GameState) -> int:
        """
        FarthestFoodAndExit heuristic as described in the requirements.
        This is the main heuristic function from heuristic.py integrated into this class.
        """
        pacman_pos = state.pacman.pos
        food_set = frozenset(state.food_left)
        step_count = state.step_count
        exit_pos = self._get_current_exit_pos(step_count)

        # Case 1: All food is eaten.
        # The only remaining task is to go to the exit.
        if len(food_set) == 0:
            return self._memoized_bfs_distance(pacman_pos, exit_pos)

        # Case 2: Food remains.
        # h(n) must underestimate the true cost.
        # True Cost >= Cost to get to the FARTHEST food dot.
        # True Cost >= Cost from SOME food dot to the exit (the last one).
        
        # Relaxation 1: Cost to get to the farthest food dot from Pacman
        dist_to_farthest_food = 0
        for food in food_set:
            dist = self._memoized_bfs_distance(pacman_pos, food)
            if dist > dist_to_farthest_food:
                dist_to_farthest_food = dist
                
        # Relaxation 2: Cost from the *closest* food dot to the exit
        # The true path must end with (some_food -> exit). The
        # minimum possible cost for this last leg is this value.
        dist_from_food_to_exit = 999999
        for food in food_set:
            dist = self._memoized_bfs_distance(food, exit_pos)
            if dist < dist_from_food_to_exit:
                dist_from_food_to_exit = dist

        # The total cost must be at least as much as both of these
        # separate relaxed problems. Therefore, we can take the max.
        return max(dist_to_farthest_food, dist_from_food_to_exit)
    
    def _memoized_bfs_distance(self, start: Tuple[int, int], end: Tuple[int, int]) -> int:
        """
        Memoized BFS distance calculation from heuristic.py.
        Uses BFS to find shortest path, respecting walls.
        """
        cache_key = (start, end)
        if cache_key in self._distance_cache:
            return self._distance_cache[cache_key]
        
        if start == end:
            self._distance_cache[cache_key] = 0
            return 0
        
        # BFS to find shortest path
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            pos, dist = queue.popleft()
            
            if pos == end:
                self._distance_cache[cache_key] = dist
                return dist
            
            # Check all 4 directions
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_pos = (pos[0] + dr, pos[1] + dc)
                
                if (new_pos not in visited and 
                    0 <= new_pos[0] < self.grid.rows and 0 <= new_pos[1] < self.grid.cols and
                    not self.grid.is_wall(new_pos)):
                    visited.add(new_pos)
                    queue.append((new_pos, dist + 1))
        
        # No path found
        self._distance_cache[cache_key] = float('inf')
        return float('inf')
    
    def _get_current_exit_pos(self, step_count: int) -> Tuple[int, int]:
        """
        Get the current exit position considering maze rotation.
        """
        # Calculate rotation count
        rotation_count = step_count // 30
        
        # Get base exit position
        base_exit = self.grid.exitgate_pos
        if base_exit is None:
            return (9, 9)  # Default fallback
        
        # Apply rotations
        r, c = base_exit
        for _ in range(rotation_count % 4):  # 4 rotations = 360 degrees
            r, c = c, self.grid.rows - 1 - r
        
        return (r, c)
