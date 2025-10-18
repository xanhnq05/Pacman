# pacman/search/astar_complete.py
"""
Complete A* implementation for Pacman following the exact requirements.
Implements proper state space formulation and FarthestFoodAndExit heuristic.
"""

import heapq
from collections import deque
from typing import List, Tuple, Optional, Set, Dict, Any
from pacman.core.state import GameState
from pacman.core.entities import Pacman, Ghost
from pacman.core.grid import Grid
from pacman.core.rules import Rules
from pacman.search.heuristics import Heuristics


class AStarComplete:
    """
    Complete A* implementation with proper state space formulation.
    State: (pacman_pos, food_set, ghost_states, pie_steps, step_count)
    """
    
    def __init__(self, grid: Grid, rules: Rules):
        self.grid = grid
        self.rules = rules
        self.distance_cache: Dict[Tuple[Tuple[int, int], Tuple[int, int]], int] = {}
        self.heuristics = Heuristics(grid)
        
    def search(self, initial_state: GameState) -> Optional[List[Tuple[int, int]]]:
        """
        Perform A* search to find optimal path.
        
        Returns:
            List of actions (dr, dc) to reach goal, or None if no path exists
        """
        # Convert GameState to tuple format for A* search
        initial_tuple_state = self._gamestate_to_tuple(initial_state)
        
        # Priority queue: (f_cost, g_cost, state_counter, state, path)
        state_counter = 0
        frontier = [(0, 0, state_counter, initial_tuple_state, [])]
        heapq.heapify(frontier)
        state_counter += 1
        
        # Closed set to avoid revisiting states
        closed: Set[Tuple] = set()
        
        # Track best g_cost for each state
        g_costs = {initial_tuple_state: 0}
        
        while frontier:
            f_cost, g_cost, _, current_state, path = heapq.heappop(frontier)
            
            # Check if goal is reached
            if self._is_goal_state(current_state):
                return path
            
            # Skip if already processed with better cost
            if current_state in closed:
                continue
                
            closed.add(current_state)
            
            # Generate successors
            for successor_state, action, cost in self._get_successors(current_state):
                if successor_state in closed:
                    continue
                    
                new_g_cost = g_cost + cost
                
                # Calculate heuristic
                h_cost = self._calculate_heuristic(successor_state)
                new_f_cost = new_g_cost + h_cost
                
                # Only add if we found a better path to this state
                if successor_state not in g_costs or new_g_cost < g_costs[successor_state]:
                    g_costs[successor_state] = new_g_cost
                    new_path = path + [action]
                    heapq.heappush(frontier, (new_f_cost, new_g_cost, state_counter, successor_state, new_path))
                    state_counter += 1
        
        return None  # No path found
    
    def _gamestate_to_tuple(self, state: GameState) -> Tuple:
        """
        Convert GameState to tuple format for A* search.
        State format: (pacman_pos, food_set, ghost_states, pie_steps, step_count)
        """
        pacman_pos = state.pacman.pos
        food_set = frozenset(state.food_left)
        ghost_states = tuple((ghost.pos, ghost.direction) for ghost in state.ghosts)
        pie_steps = state.pacman.power_steps
        step_count = state.step_count
        
        return (pacman_pos, food_set, ghost_states, pie_steps, step_count)
    
    def _tuple_to_gamestate(self, tuple_state: Tuple) -> GameState:
        """
        Convert tuple state back to GameState for processing.
        """
        pacman_pos, food_set, ghost_states, pie_steps, step_count = tuple_state
        
        # Create Pacman object
        pacman = Pacman(pacman_pos, power_steps=pie_steps)
        
        # Create Ghost objects
        ghosts = []
        for ghost_pos, ghost_direction in ghost_states:
            ghosts.append(Ghost(ghost_pos, "red", ghost_direction))  # Default color
        
        return GameState(
            pacman=pacman,
            ghosts=tuple(ghosts),
            food_left=food_set,
            pies_left=frozenset(),  # Simplified for now
            step_count=step_count
        )
    
    def _is_goal_state(self, state: Tuple) -> bool:
        """
        Check if state is a goal state.
        Goal: Pacman at exit gate AND no food left.
        """
        pacman_pos, food_set, _, _, _ = state
        exit_pos = self._get_current_exit_pos(state[4])
        
        return pacman_pos == exit_pos and len(food_set) == 0
    
    def _get_current_exit_pos(self, step_count: int) -> Tuple[int, int]:
        """
        Get current exit position considering maze rotation.
        """
        # Check if maze should rotate (every 30 steps)
        if step_count % 30 == 0 and step_count > 0:
            # Calculate rotated exit position
            # This is a simplified version - in practice, you'd track rotation state
            return self._rotate_position(self.grid.exitgate_pos, step_count // 30)
        return self.grid.exitgate_pos
    
    def _rotate_position(self, pos: Tuple[int, int], rotation_count: int) -> Tuple[int, int]:
        """
        Rotate position by 90 degrees right, rotation_count times.
        """
        r, c = pos
        for _ in range(rotation_count % 4):  # 4 rotations = 360 degrees
            r, c = c, self.grid.rows - 1 - r
        return (r, c)
    
    def _get_successors(self, state: Tuple) -> List[Tuple[Tuple, Tuple[int, int], int]]:
        """
        Generate all valid successor states.
        Returns list of (successor_state, action, cost) tuples.
        """
        pacman_pos, food_set, ghost_states, pie_steps, step_count = state
        successors = []
        
        # Calculate new step count
        new_step_count = step_count + 1
        
        # Check for maze rotation
        if new_step_count % 30 == 0:
            # Apply rotation to all positions
            pacman_pos = self._rotate_position(pacman_pos, 1)
            food_set = frozenset(self._rotate_position(food, 1) for food in food_set)
            ghost_states = tuple((self._rotate_position(ghost_pos, 1), ghost_dir) 
                                for ghost_pos, ghost_dir in ghost_states)
        
        # Update ghost positions
        new_ghost_states = self._update_ghost_positions(ghost_states)
        
        # Try all 4 directions + teleport
        actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # North, South, East, West
        
        # Add teleport actions if at teleport corner
        if self.grid.is_teleport_corner(pacman_pos):
            teleport_destinations = self.grid.get_teleport_destinations(pacman_pos)
            for dest in teleport_destinations:
                dr = dest[0] - pacman_pos[0]
                dc = dest[1] - pacman_pos[1]
                actions.append((dr, dc))
        
        for action in actions:
            dr, dc = action
            new_pacman_pos = (pacman_pos[0] + dr, pacman_pos[1] + dc)
            
            # Check bounds
            if not (0 <= new_pacman_pos[0] < self.grid.rows and 
                   0 <= new_pacman_pos[1] < self.grid.cols):
                continue
            
            # Check wall collision
            is_wall = self.grid.is_wall(new_pacman_pos)
            if is_wall and pie_steps <= 0:
                continue  # Cannot move through wall without pie
            
            # Check ghost collision
            if self._check_ghost_collision(new_pacman_pos, new_ghost_states):
                continue  # Lose state - skip
            
            # Update food and pie steps
            new_food_set = food_set
            new_pie_steps = pie_steps
            
            if new_pacman_pos in new_food_set:
                new_food_set = new_food_set - {new_pacman_pos}
            
            # Check for magical pie
            if new_pacman_pos in self.grid.initial_magical_pie:
                new_pie_steps = 5  # Activate power mode
            elif new_pie_steps > 0:
                new_pie_steps -= 1
            
            # Create new state
            new_state = (new_pacman_pos, new_food_set, new_ghost_states, new_pie_steps, new_step_count)
            successors.append((new_state, action, 1))  # All actions cost 1
        
        return successors
    
    def _update_ghost_positions(self, ghost_states: Tuple) -> Tuple:
        """
        Update ghost positions based on their movement logic.
        """
        new_ghost_states = []
        
        for ghost_pos, ghost_direction in ghost_states:
            dr, dc = ghost_direction
            new_ghost_pos = (ghost_pos[0], ghost_pos[1] + dc)  # Ghosts move horizontally only
            
            # Check for wall collision
            if self.grid.is_wall(new_ghost_pos):
                # Reverse direction
                new_direction = (dr, -dc)
                new_ghost_pos = ghost_pos  # Stay in place
            else:
                new_direction = ghost_direction
            
            new_ghost_states.append((new_ghost_pos, new_direction))
        
        return tuple(new_ghost_states)
    
    def _check_ghost_collision(self, pacman_pos: Tuple[int, int], ghost_states: Tuple) -> bool:
        """
        Check if Pacman collides with any ghost.
        """
        for ghost_pos, _ in ghost_states:
            if pacman_pos == ghost_pos:
                return True
        return False
    
    def _calculate_heuristic(self, state: Tuple) -> float:
        """
        Calculate heuristic using the FarthestFoodAndExit method.
        """
        # Convert tuple state to GameState for heuristic calculation
        game_state = self._tuple_to_gamestate(state)
        return self.heuristics.farthest_food_and_exit_heuristic(game_state)
    
    def _memoized_bfs_distance(self, start: Tuple[int, int], end: Tuple[int, int]) -> int:
        """
        Memoized BFS distance calculation.
        """
        cache_key = (start, end)
        if cache_key in self.distance_cache:
            return self.distance_cache[cache_key]
        
        if start == end:
            self.distance_cache[cache_key] = 0
            return 0
        
        # BFS to find shortest path
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            pos, dist = queue.popleft()
            
            if pos == end:
                self.distance_cache[cache_key] = dist
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
        
        # No path found
        self.distance_cache[cache_key] = float('inf')
        return float('inf')
