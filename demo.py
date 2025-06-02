from datetime import datetime, timedelta
from src.drone import Drone, Waypoint
from src.deconfliction import DeconflictionSystem
from src.visualization import DroneVisualizer
import os
import matplotlib.pyplot as plt

def create_demo_data():
    """Create a set of drones for demonstration"""
    # Primary drone mission
    primary_drone = Drone(
        id="primary",
        waypoints=[
            Waypoint(0, 0, 0, datetime.now()),
            Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=5)),
            Waypoint(200, 0, 100, datetime.now() + timedelta(minutes=10))
        ],
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=15)
    )

    # Simulated drones
    drones = [
        # Drone with spatial conflict
        Drone(
            id="sim1",
            waypoints=[
                Waypoint(50, 50, 25, datetime.now() + timedelta(minutes=2)),
                Waypoint(150, 150, 75, datetime.now() + timedelta(minutes=7))
            ],
            start_time=datetime.now() + timedelta(minutes=2),
            end_time=datetime.now() + timedelta(minutes=12)
        ),
        # Drone with temporal conflict
        Drone(
            id="sim2",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now() + timedelta(minutes=3)),
                Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=8))
            ],
            start_time=datetime.now() + timedelta(minutes=3),
            end_time=datetime.now() + timedelta(minutes=18)
        ),
        # Non-conflicting drone
        Drone(
            id="sim3",
            waypoints=[
                Waypoint(250, 250, 150, datetime.now() + timedelta(minutes=1)),
                Waypoint(350, 350, 200, datetime.now() + timedelta(minutes=6))
            ],
            start_time=datetime.now() + timedelta(minutes=1),
            end_time=datetime.now() + timedelta(minutes=11)
        )
    ]
    return primary_drone, drones

def run_demo():
    # Create output directory for visualizations
    output_dir = "demo_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create demo data
    primary_drone, drones = create_demo_data()

    # Initialize deconfliction system
    deconfliction_system = DeconflictionSystem(safety_buffer=10.0)

    # Add simulated drones
    for drone in drones:
        deconfliction_system.add_simulated_drone(drone)

    # Validate primary drone's mission
    print("\nValidating primary drone's mission...")
    results = deconfliction_system.validate_mission(primary_drone)
    print(f"Validation Status: {results['status']}")
    
    if results['status'] == 'conflict':
        print("\nConflicts detected:")
        explanation = deconfliction_system.get_conflict_explanation(results)
        print(explanation)

    # Visualize results
    visualizer = DroneVisualizer()
    
    # Plot trajectories
    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection='3d')
    
    # Plot primary drone
    visualizer.plot_3d_trajectory(primary_drone, ax=ax, color='blue', 
                                label='Primary Drone', show=False)
    
    # Plot simulated drones
    colors = ['green', 'orange', 'purple']
    for i, drone in enumerate(drones):
        visualizer.plot_3d_trajectory(drone, ax=ax, color=colors[i], 
                                    label=f'Simulated Drone {i+1}', show=False)
    
    # Add conflict points if any
    if results['status'] == 'conflict':
        conflict_points = []
        for conflict in results['conflicts']:
            conflict_points.extend(conflict['conflict_locations'])
        x_conf, y_conf, z_conf = zip(*conflict_points)
        ax.scatter(x_conf, y_conf, z_conf, color='red', s=100, 
                  marker='x', label='Conflict Points')
    
    plt.legend()
    plt.title('Drone Trajectories with Conflict Points')
    plt.savefig(os.path.join(output_dir, 'trajectories.png'))
    plt.close()
    
    # Create animation
    print("\nCreating animation...")
    visualizer.create_animation([primary_drone] + drones, 
                              conflict_points=conflict_points if results['status'] == 'conflict' else None,
                              output_dir=output_dir)
    
    print(f"\nVisualization files saved to: {output_dir}")
    print("- trajectories.png: Static 3D visualization of trajectories")
    print("- drone_animation.gif: Animated visualization showing drone movements")

if __name__ == "__main__":
    run_demo()
