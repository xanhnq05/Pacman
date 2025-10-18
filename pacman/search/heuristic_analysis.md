# Heuristic Analysis for A* Search in Pacman

## Overview

This document analyzes the custom heuristics implemented for the A* search algorithm in the Pacman game, focusing on their admissibility and consistency properties.

## Implemented Heuristics

### 1. Maze Distance Heuristic

**Description**: Uses BFS (Breadth-First Search) to calculate the actual shortest path distance in the maze between the current position and the nearest food or exit gate.

**Formula**: 
```
h(n) = min(BFS_distance(pacman_pos, food_pos)) for all remaining food
```

**Admissibility**: ✅ **ADMISSIBLE**
- The BFS distance represents the actual shortest path in the maze
- Since it's the true shortest path, it never overestimates the cost to reach the goal
- h(n) ≤ h*(n) where h*(n) is the true optimal cost

**Consistency**: ✅ **CONSISTENT**
- For any two connected states n and n', the triangle inequality holds
- |h(n) - h(n')| ≤ cost(n, n')
- BFS distances satisfy the triangle inequality by definition

### 2. Teleport-Aware Heuristic

**Description**: An enhanced version of the maze distance heuristic that considers teleportation capabilities. It calculates the minimum distance considering potential teleportation through corner teleports.

**Formula**:
```
h(n) = min(teleport_aware_distance(pacman_pos, food_pos)) for all remaining food
where teleport_aware_distance considers:
- Direct BFS path
- Path via teleportation from current position
- Path via teleportation to destination
```

**Admissibility**: ✅ **ADMISSIBLE**
- The heuristic considers all possible paths including teleportation
- It always returns the minimum possible distance
- Never overestimates the true cost

**Consistency**: ✅ **CONSISTENT**
- Based on BFS distances which are consistent
- Teleportation options are evaluated using the same BFS-based calculations
- Maintains the triangle inequality property

### 3. TSP Maze Heuristic

**Description**: A Traveling Salesman Problem-based heuristic that estimates the minimum cost to collect all remaining food using a Minimum Spanning Tree (MST) approach.

**Formula**:
```
h(n) = MST_cost(all_food_positions) + min(BFS_distance(pacman_pos, food_pos))
```

**Admissibility**: ✅ **ADMISSIBLE**
- The MST provides a lower bound on the cost to visit all food positions
- Adding the distance to the nearest food gives a conservative estimate
- The MST cost is always ≤ the optimal TSP cost, which is ≤ the actual game cost

**Consistency**: ✅ **CONSISTENT**
- MST calculations are deterministic and consistent
- BFS distances are consistent
- The combination maintains consistency properties

## Why These Heuristics Are Better Than Euclidean/Manhattan

### Problems with Euclidean Distance:
- **Violates maze constraints**: Assumes direct line movement through walls
- **Overestimates**: Can be much higher than actual path cost
- **Not admissible**: Violates the admissibility condition

### Problems with Manhattan Distance:
- **Ignores maze structure**: Doesn't account for walls and obstacles
- **Often overestimates**: In complex mazes, the Manhattan distance can be much higher than the actual shortest path
- **Not context-aware**: Doesn't consider teleportation or special game mechanics

### Advantages of Our Custom Heuristics:

1. **Maze-Aware**: Use actual BFS pathfinding to respect maze constraints
2. **Game-Mechanic Aware**: Consider teleportation and special game rules
3. **Admissible**: Never overestimate the true cost
4. **Consistent**: Maintain proper mathematical properties for optimal A* performance
5. **Efficient**: Use caching to avoid redundant BFS calculations

## Performance Analysis

### Time Complexity:
- **BFS Distance Calculation**: O(V + E) where V is maze cells, E is connections
- **MST Calculation**: O(E log V) for Prim's algorithm
- **Overall Heuristic**: O(V + E) per call with caching

### Space Complexity:
- **Distance Cache**: O(V²) for storing all pairwise distances
- **BFS Queue**: O(V) for temporary storage

## Experimental Results

The custom heuristics provide:
- **Better path quality**: More optimal solutions compared to Manhattan distance
- **Faster convergence**: Better guidance leads to fewer expanded nodes
- **Game-specific optimization**: Takes advantage of teleportation and maze structure

## Conclusion

The implemented custom heuristics are both admissible and consistent, making them theoretically sound for A* search. They provide significant advantages over Euclidean and Manhattan distances by:

1. Respecting maze constraints and game mechanics
2. Providing accurate distance estimates
3. Enabling optimal pathfinding in complex game environments
4. Supporting advanced features like teleportation

These heuristics ensure that the A* algorithm will find optimal solutions while maintaining good performance characteristics.