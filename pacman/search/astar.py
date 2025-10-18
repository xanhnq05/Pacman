# pacman/search/astar.py
"""
A* search algorithm implementation for Pacman pathfinding.
Reusable and independent of pygame.
"""

from pacman.core.state import GameState
from pacman.core.rules import Rules
from pacman.search.heuristics import Heuristics
import heapq
from typing import List, Tuple, Optional, Set


class AStarSearch:
    """
    A* search implementation for finding optimal path in Pacman game.
    """
    
    def __init__(self, rules: Rules, heuristics: Heuristics, heuristic_type="maze_distance"):
        self.rules = rules
        self.heuristics = heuristics
        self.heuristic_type = heuristic_type
        
    def search(self, initial_state: GameState, goal_condition) -> Optional[List[Tuple[int, int]]]:
        """
        Perform A* search to find optimal path.
        
        Args:
            initial_state: Starting game state
            goal_condition: Function that takes a state and returns True if goal is reached
            
        Returns:
            List of actions (dr, dc) to reach goal, or None if no path exists
        """
        # Priority queue: (f_cost, g_cost, state_counter, state, path)
        # Use counter to break ties and avoid comparing GameState objects
        state_counter = 0
        frontier = [(0, 0, state_counter, initial_state, [])]
        heapq.heapify(frontier)
        state_counter += 1
        
        # Closed set to avoid revisiting states
        closed: Set[GameState] = set()
        
        # Track best g_cost for each state
        g_costs = {initial_state: 0}
        
        while frontier:
            f_cost, g_cost, _, current_state, path = heapq.heappop(frontier)
            
            # Check if goal is reached
            if goal_condition(current_state):
                return path
            
            # Skip if already processed with better cost
            if current_state in closed:
                continue
                
            closed.add(current_state)
            
            # Generate successors
            for action in self._get_valid_actions(current_state):
                successor_state = self.rules.get_successor_for_astar(current_state, action)
                
                if successor_state in closed:
                    continue
                    
                # Calculate cost based on action type
                if self._is_teleport_action(current_state.pacman.pos, action):
                    new_g_cost = g_cost + 1  # Teleport cost is 1
                else:
                    new_g_cost = g_cost + 1  # Normal move cost is 1
                
                # Use the specified heuristic type
                if self.heuristic_type == "maze_distance":
                    new_h_cost = self.heuristics.maze_distance_heuristic(successor_state)
                elif self.heuristic_type == "teleport_aware":
                    new_h_cost = self.heuristics.teleport_aware_heuristic(successor_state)
                elif self.heuristic_type == "tsp_maze":
                    new_h_cost = self.heuristics.tsp_maze_heuristic(successor_state)
                elif self.heuristic_type == "farthest_food_and_exit":
                    new_h_cost = self.heuristics.farthest_food_and_exit_heuristic(successor_state)
                else:
                    new_h_cost = self.heuristics.maze_distance_heuristic(successor_state)
                
                new_f_cost = new_g_cost + new_h_cost
                
                # Only add if we found a better path to this state
                if successor_state not in g_costs or new_g_cost < g_costs[successor_state]:
                    g_costs[successor_state] = new_g_cost
                    new_path = path + [action]
                    heapq.heappush(frontier, (new_f_cost, new_g_cost, state_counter, successor_state, new_path))
                    state_counter += 1
        
        return None  # No path found
    
    def _get_valid_actions(self, state: GameState) -> List[Tuple[int, int]]:
        """
        Get all valid actions from current state.
        Returns list of (dr, dc) tuples.
        """
        actions = []
        pacman_pos = state.pacman.pos
        
        # Check all 4 directions
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_pos = (pacman_pos[0] + dr, pacman_pos[1] + dc)
            
            # Check if move is valid (not into wall, unless in power mode)
            if not self.rules.grid.is_wall(new_pos) or state.pacman.power_steps > 0:
                actions.append((dr, dc))
        
        # Add teleport actions if at teleport corner
        if self.rules.grid.is_teleport_corner(pacman_pos):
            teleport_destinations = self.rules.grid.get_teleport_destinations(pacman_pos)
            for dest in teleport_destinations:
                # Add special teleport action (represented as large offset)
                dr = dest[0] - pacman_pos[0]
                dc = dest[1] - pacman_pos[1]
                actions.append((dr, dc))
                
        return actions
    
    def _is_teleport_action(self, current_pos, action):
        """
        Kiểm tra xem action có phải là teleport không.
        """
        dr, dc = action
        new_pos = (current_pos[0] + dr, current_pos[1] + dc)
        
        # Nếu di chuyển đến góc teleport, đó là teleport action
        return self.rules.grid.is_teleport_corner(new_pos)
