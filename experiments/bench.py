# experiments/bench.py
"""
Benchmarking and performance measurement for Pacman search algorithms.
Measures time/space complexity (expansions, frontier size) and generates charts.
"""

import time
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple
from pacman.core.grid import Grid
from pacman.core.state import GameState
from pacman.core.rules import Rules
from pacman.search.astar import AStarSearch
from pacman.search.heuristics import Heuristics


class BenchmarkResults:
    """
    Container for benchmark results.
    """
    def __init__(self):
        self.algorithm_name = ""
        self.heuristic_name = ""
        self.execution_time = 0.0
        self.nodes_expanded = 0
        self.max_frontier_size = 0
        self.path_length = 0
        self.success = False
        self.memory_usage = 0


class PacmanBenchmark:
    """
    Benchmarking suite for Pacman search algorithms.
    """
    
    def __init__(self):
        self.results: List[BenchmarkResults] = []
        
    def run_single_benchmark(self, 
                           layout_file: str, 
                           algorithm: str = "astar",
                           heuristic: str = "manhattan") -> BenchmarkResults:
        """
        Run a single benchmark test.
        
        Args:
            layout_file: Path to layout file
            algorithm: Search algorithm to use
            heuristic: Heuristic function to use
            
        Returns:
            BenchmarkResults object with performance metrics
        """
        result = BenchmarkResults()
        result.algorithm_name = algorithm
        result.heuristic_name = heuristic
        
        try:
            # Initialize game components
            grid = Grid(layout_file)
            initial_state = GameState.get_initial_state(grid)
            rules = Rules(grid)
            heuristics = Heuristics(grid)
            
            # Create search algorithm
            if algorithm == "astar":
                search = AStarSearch(rules, heuristics)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Define goal condition (collect all food and reach exit)
            def goal_condition(state):
                return (len(state.food_left) == 0 and 
                       state.pacman.pos == grid.exitgate_pos)
            
            # Measure performance
            start_time = time.time()
            path = search.search(initial_state, goal_condition)
            end_time = time.time()
            
            result.execution_time = end_time - start_time
            result.success = path is not None
            result.path_length = len(path) if path else 0
            
            # TODO: Add actual node expansion counting
            # This would require modifying the search algorithm to track metrics
            result.nodes_expanded = 0  # Placeholder
            result.max_frontier_size = 0  # Placeholder
            
        except Exception as e:
            print(f"Benchmark failed: {e}")
            result.success = False
            
        return result
    
    def run_benchmark_suite(self, layout_files: List[str]) -> List[BenchmarkResults]:
        """
        Run benchmark suite on multiple layouts.
        
        Args:
            layout_files: List of layout file paths
            
        Returns:
            List of benchmark results
        """
        results = []
        
        algorithms = ["astar"]
        heuristics = ["manhattan", "bfs", "mst"]
        
        for layout_file in layout_files:
            print(f"Benchmarking layout: {layout_file}")
            
            for algorithm in algorithms:
                for heuristic in heuristics:
                    print(f"  Testing {algorithm} with {heuristic} heuristic...")
                    result = self.run_single_benchmark(layout_file, algorithm, heuristic)
                    results.append(result)
        
        self.results.extend(results)
        return results
    
    def generate_charts(self, output_dir: str = "experiments/charts"):
        """
        Generate performance charts from benchmark results.
        
        Args:
            output_dir: Directory to save chart images
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if not self.results:
            print("No results to plot")
            return
        
        # Extract data for plotting
        algorithms = list(set(r.algorithm_name for r in self.results))
        heuristics = list(set(r.heuristic_name for r in self.results))
        
        # Execution time comparison
        self._plot_execution_times(heuristics, output_dir)
        
        # Success rate comparison
        self._plot_success_rates(heuristics, output_dir)
        
        # Path length comparison
        self._plot_path_lengths(heuristics, output_dir)
    
    def _plot_execution_times(self, heuristics: List[str], output_dir: str):
        """Plot execution time comparison."""
        plt.figure(figsize=(10, 6))
        
        for heuristic in heuristics:
            times = [r.execution_time for r in self.results 
                    if r.heuristic_name == heuristic and r.success]
            if times:
                plt.hist(times, alpha=0.7, label=f"{heuristic} heuristic", bins=20)
        
        plt.xlabel("Execution Time (seconds)")
        plt.ylabel("Frequency")
        plt.title("Execution Time Distribution by Heuristic")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{output_dir}/execution_times.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_success_rates(self, heuristics: List[str], output_dir: str):
        """Plot success rate comparison."""
        plt.figure(figsize=(10, 6))
        
        success_rates = []
        for heuristic in heuristics:
            total = len([r for r in self.results if r.heuristic_name == heuristic])
            successful = len([r for r in self.results 
                            if r.heuristic_name == heuristic and r.success])
            success_rate = (successful / total * 100) if total > 0 else 0
            success_rates.append(success_rate)
        
        bars = plt.bar(heuristics, success_rates, color=['blue', 'green', 'red'])
        plt.xlabel("Heuristic Function")
        plt.ylabel("Success Rate (%)")
        plt.title("Success Rate by Heuristic")
        plt.ylim(0, 100)
        
        # Add value labels on bars
        for bar, rate in zip(bars, success_rates):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{output_dir}/success_rates.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_path_lengths(self, heuristics: List[str], output_dir: str):
        """Plot path length comparison."""
        plt.figure(figsize=(10, 6))
        
        for heuristic in heuristics:
            lengths = [r.path_length for r in self.results 
                      if r.heuristic_name == heuristic and r.success]
            if lengths:
                plt.hist(lengths, alpha=0.7, label=f"{heuristic} heuristic", bins=20)
        
        plt.xlabel("Path Length")
        plt.ylabel("Frequency")
        plt.title("Path Length Distribution by Heuristic")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{output_dir}/path_lengths.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def print_summary(self):
        """Print benchmark summary."""
        if not self.results:
            print("No benchmark results available")
            return
        
        print("\n=== PACMAN SEARCH BENCHMARK SUMMARY ===")
        print(f"Total tests: {len(self.results)}")
        
        successful = len([r for r in self.results if r.success])
        print(f"Successful: {successful} ({successful/len(self.results)*100:.1f}%)")
        
        if successful > 0:
            avg_time = np.mean([r.execution_time for r in self.results if r.success])
            avg_length = np.mean([r.path_length for r in self.results if r.success])
            print(f"Average execution time: {avg_time:.3f}s")
            print(f"Average path length: {avg_length:.1f}")
        
        # Group by heuristic
        heuristics = list(set(r.heuristic_name for r in self.results))
        for heuristic in heuristics:
            heuristic_results = [r for r in self.results if r.heuristic_name == heuristic]
            success_rate = len([r for r in heuristic_results if r.success]) / len(heuristic_results) * 100
            print(f"\n{heuristic} heuristic: {success_rate:.1f}% success rate")


def main():
    """
    Main function to run benchmarks.
    """
    benchmark = PacmanBenchmark()
    
    # Test layouts (you can add more)
    layout_files = [
        "data/layout.txt",
        # Add more layouts here
    ]
    
    print("Starting Pacman Search Benchmark...")
    results = benchmark.run_benchmark_suite(layout_files)
    
    # Generate charts
    benchmark.generate_charts()
    
    # Print summary
    benchmark.print_summary()


if __name__ == "__main__":
    main()
