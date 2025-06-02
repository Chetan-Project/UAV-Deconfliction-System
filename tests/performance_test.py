import os
import sys
import time
import logging
import random
from datetime import datetime, timedelta

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.deconfliction import DeconflictionSystem
from src.drone import Drone, Waypoint
from src.conflict import ConflictPoint

def generate_random_drone(id_prefix: str, num_waypoints: int = 5) -> Drone:
    """Generate a random drone with waypoints"""
    waypoints = []
    current_time = datetime.now()
    
    for i in range(num_waypoints):
        # Generate random coordinates
        x = random.uniform(-1000, 1000)
        y = random.uniform(-1000, 1000)
        z = random.uniform(0, 1000)  # Altitude between 0-1000 meters
        
        # Add some time variation
        time_offset = timedelta(minutes=i * 5)
        waypoint_time = current_time + time_offset
        
        waypoints.append(Waypoint(x, y, z, waypoint_time))
    
    # Calculate start and end times from waypoints
    start_time = min(wp.timestamp for wp in waypoints)
    end_time = max(wp.timestamp for wp in waypoints)
    
    return Drone(f"{id_prefix}_{i}", waypoints, start_time, end_time)

def run_performance_test():
    """Run performance benchmark test"""
    logging.basicConfig(level=logging.INFO)
    system = DeconflictionSystem()
    
    # Test parameters
    num_drones = [10, 50, 100, 500, 1000]
    results = []
    
    for n in num_drones:
        logging.info(f"Testing with {n} drones...")
        
        # Generate random drones
        drones = [generate_random_drone(f"drone_{i}", random.randint(3, 10)) for i in range(n)]
        
        # Add drones to system
        for drone in drones:
            system.add_simulated_drone(drone)
        
        # Validate a mission
        start_time = time.time()
        validation_result = system.validate_mission(drones[0])
        end_time = time.time()
        
        execution_time = end_time - start_time
        results.append({
            "num_drones": n,
            "execution_time": execution_time,
            "status": validation_result["status"],
            "conflicts": len(validation_result["conflicts"]),
            "cache_size": len(system.conflict_cache)
        })
        
        # Clear system for next test
        system = DeconflictionSystem()
        
    return results

def print_performance_results(results):
    """Print performance test results"""
    print("\nPerformance Benchmark Results:")
    print("-" * 80)
    print(f"{'Number of Drones':<15} {'Execution Time (s)':<20} {'Conflicts':<10} {'Cache Size':<10}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['num_drones']:<15} {result['execution_time']:<20.4f} {result['conflicts']:<10} {result['cache_size']:<10}")

if __name__ == "__main__":
    results = run_performance_test()
    print_performance_results(results)
