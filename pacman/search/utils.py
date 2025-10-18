# pacman/search/utils.py
"""
Utility functions for search algorithms.
Includes BFS maze distance, MST calculation, and memoization helpers.
"""

from typing import Dict, Tuple, List, Set
from collections import deque
import heapq
from functools import lru_cache


class SearchUtils:
    """
    Utility functions for search algorithms.
    """
    
    def __init__(self, grid):
        self.grid = grid
        self._distance_cache: Dict[Tuple[Tuple[int, int], Tuple[int, int]], int] = {}
    
    def bfs_maze_distance(self, start: Tuple[int, int], goal: Tuple[int, int]) -> int:
        """
        Calculate actual maze distance using BFS.
        Caches results for efficiency.
        """
        cache_key = (start, goal)
        if cache_key in self._distance_cache:
            return self._distance_cache[cache_key]
        
        # BFS to find shortest path
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            pos, dist = queue.popleft()
            
            if pos == goal:
                self._distance_cache[cache_key] = dist
                return dist
            
            # Check all 4 directions
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_pos = (pos[0] + dr, pos[1] + dc)
                
                if (new_pos not in visited and 
                    not self.grid.is_wall(new_pos)):
                    visited.add(new_pos)
                    queue.append((new_pos, dist + 1))
        
        # No path found
        self._distance_cache[cache_key] = float('inf')
        return float('inf')
    
    def calculate_mst(self, positions: List[Tuple[int, int]]) -> int:
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
                dist = self.bfs_maze_distance(pos1, pos2)
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
    
    def clear_cache(self):
        """Clear the distance cache."""
        self._distance_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'cached_distances': len(self._distance_cache),
            'cache_hits': getattr(self, '_cache_hits', 0),
            'cache_misses': getattr(self, '_cache_misses', 0)
        }


def memoize(func):
    """
    Simple memoization decorator for expensive computations.
    """
    cache = {}
    
    def wrapper(*args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper


@lru_cache(maxsize=1000)
def cached_manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """
    Cached Manhattan distance calculation.
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
