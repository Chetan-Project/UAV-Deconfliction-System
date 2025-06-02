import logging
from datetime import datetime, timedelta
from src.drone import Drone, Waypoint
from src.deconfliction import DeconflictionSystem
from src.visualization import DroneVisualizer
import os
import matplotlib.pyplot as plt
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class UAVDemonstration:
    def __init__(self, output_dir="demonstration_output"):
        """Initialize the demonstration system"""
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.visualizer = DroneVisualizer()
        self.system = DeconflictionSystem(safety_buffer=10.0)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialized UAV Demonstration System")
        
    def create_scenario(self, scenario_name: str, primary_drone: Drone, simulated_drones: list):
        """
        Create and validate a scenario
        
        Args:
            scenario_name: Name of the scenario
            primary_drone: The primary drone's mission
            simulated_drones: List of simulated drones
        """
        self.logger.info(f"Creating scenario: {scenario_name}")
        print(f"\n=== Scenario: {scenario_name} ===")
        
        # Add simulated drones
        for drone in simulated_drones:
            self.system.add_simulated_drone(drone)
            self.logger.info(f"Added simulated drone {drone.id}")
        
        # Validate primary drone's mission
        results = self.system.validate_mission(primary_drone)
        print(f"Validation Status: {results['status']}")
        
        if results['status'] == 'conflict':
            print("\nConflicts detected:")
            explanation = self.system.get_conflict_explanation(results)
            print(explanation)
            
        # Create visualization
        self.visualize_scenario(scenario_name, primary_drone, simulated_drones, results)
        return results
        
    def visualize_scenario(self, scenario_name: str, primary_drone: Drone, 
                         simulated_drones: list, results: dict):
        """
        Create visualizations for the scenario
        
        Args:
            scenario_name: Name of the scenario
            primary_drone: The primary drone's mission
            simulated_drones: List of simulated drones
            results: Validation results
        """
        plt.figure(figsize=(12, 8))
        ax = plt.axes(projection='3d')
        
        # Plot primary drone
        self.visualizer.plot_3d_trajectory(primary_drone, ax=ax, color='blue', 
                                        label='Primary Drone', show=False)
        
        # Plot simulated drones
        colors = ['green', 'orange', 'purple', 'red', 'cyan']
        for i, drone in enumerate(simulated_drones):
            self.visualizer.plot_3d_trajectory(drone, ax=ax, color=colors[i % len(colors)], 
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
        plt.title(f'{scenario_name} - Drone Trajectories')
        plt.savefig(os.path.join(self.output_dir, f'{scenario_name}_trajectories.png'))
        plt.close()
        
        # Create animation
        print(f"\nCreating animation for {scenario_name}...")
        self.visualizer.create_animation(
            [primary_drone] + simulated_drones,
            conflict_points=conflict_points if results['status'] == 'conflict' else None,
            output_dir=self.output_dir,
            filename=f'{scenario_name}_animation.gif'
        )
        
    def run_demonstration(self):
        """Run all demonstration scenarios"""
        print("Starting UAV Deconfliction System Demonstration\n")
        
        # Scenario 1: Conflict-Free Mission
        print("\n=== Scenario 1: Conflict-Free Mission ===")
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

        drones = [
            Drone(
                id="sim1",
                waypoints=[
                    Waypoint(250, 250, 150, datetime.now() + timedelta(minutes=1)),
                    Waypoint(350, 350, 200, datetime.now() + timedelta(minutes=6))
                ],
                start_time=datetime.now() + timedelta(minutes=1),
                end_time=datetime.now() + timedelta(minutes=11)
            )
        ]
        
        self.create_scenario("Scenario1_ConflictFree", primary_drone, drones)
        
        # Scenario 2: Spatial Conflict
        print("\n=== Scenario 2: Spatial Conflict ===")
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

        drones = [
            Drone(
                id="sim1",
                waypoints=[
                    Waypoint(50, 50, 25, datetime.now() + timedelta(minutes=2)),
                    Waypoint(150, 150, 75, datetime.now() + timedelta(minutes=7))
                ],
                start_time=datetime.now() + timedelta(minutes=2),
                end_time=datetime.now() + timedelta(minutes=12)
            )
        ]
        
        self.create_scenario("Scenario2_SpatialConflict", primary_drone, drones)
        
        # Scenario 3: Temporal Conflict
        print("\n=== Scenario 3: Temporal Conflict ===")
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

        drones = [
            Drone(
                id="sim1",
                waypoints=[
                    Waypoint(0, 0, 0, datetime.now() + timedelta(minutes=3)),
                    Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=8))
                ],
                start_time=datetime.now() + timedelta(minutes=3),
                end_time=datetime.now() + timedelta(minutes=18)
            )
        ]
        
        self.create_scenario("Scenario3_TemporalConflict", primary_drone, drones)
        
        # Scenario 4: Full Conflict (Spatial + Temporal)
        print("\n=== Scenario 4: Full Conflict (Spatial + Temporal) ===")
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

        drones = [
            Drone(
                id="sim1",
                waypoints=[
                    Waypoint(50, 50, 25, datetime.now() + timedelta(minutes=2)),
                    Waypoint(150, 150, 75, datetime.now() + timedelta(minutes=7))
                ],
                start_time=datetime.now() + timedelta(minutes=2),
                end_time=datetime.now() + timedelta(minutes=12)
            ),
            Drone(
                id="sim2",
                waypoints=[
                    Waypoint(0, 0, 0, datetime.now() + timedelta(minutes=3)),
                    Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=8))
                ],
                start_time=datetime.now() + timedelta(minutes=3),
                end_time=datetime.now() + timedelta(minutes=18)
            )
        ]
        
        self.create_scenario("Scenario4_FullConflict", primary_drone, drones)
        
        # Scenario 5: Emergency Landing
        print("\n=== Scenario 5: Emergency Landing ===")
        primary_drone = Drone(
            id="primary",
            waypoints=[
                Waypoint(0, 0, 100, datetime.now()),
                Waypoint(50, 50, 50, datetime.now() + timedelta(minutes=2)),
                Waypoint(100, 100, 0, datetime.now() + timedelta(minutes=3))  # Emergency landing
            ],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=5)
        )

        drones = [
            Drone(
                id="sim1",
                waypoints=[
                    Waypoint(150, 150, 150, datetime.now() + timedelta(minutes=1)),
                    Waypoint(200, 200, 100, datetime.now() + timedelta(minutes=4))
                ],
                start_time=datetime.now() + timedelta(minutes=1),
                end_time=datetime.now() + timedelta(minutes=6)
            )
        ]
        
        self.create_scenario("Scenario5_EmergencyLanding", primary_drone, drones)
        
        # Scenario 6: Circular Flight Pattern
        print("\n=== Scenario 6: Circular Flight Pattern ===")
        primary_drone = Drone(
            id="primary",
            waypoints=[
                Waypoint(0, 0, 50, datetime.now()),
                Waypoint(100, 0, 50, datetime.now() + timedelta(minutes=1)),
                Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=2)),
                Waypoint(0, 100, 50, datetime.now() + timedelta(minutes=3)),
                Waypoint(0, 0, 50, datetime.now() + timedelta(minutes=4))
            ],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=5)
        )

        drones = [
            Drone(
                id="sim1",
                waypoints=[
                    Waypoint(-50, -50, 50, datetime.now() + timedelta(minutes=0.5)),
                    Waypoint(50, -50, 50, datetime.now() + timedelta(minutes=1.5)),
                    Waypoint(50, 50, 50, datetime.now() + timedelta(minutes=2.5)),
                    Waypoint(-50, 50, 50, datetime.now() + timedelta(minutes=3.5)),
                    Waypoint(-50, -50, 50, datetime.now() + timedelta(minutes=4.5))
                ],
                start_time=datetime.now() + timedelta(minutes=0.5),
                end_time=datetime.now() + timedelta(minutes=6)
            )
        ]
        
        self.create_scenario("Scenario6_CircularFlight", primary_drone, drones)
        
        # Scenario 7: Vertical Stacking
        print("\n=== Scenario 7: Vertical Stacking ===")
        primary_drone = Drone(
            id="primary",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now()),
                Waypoint(0, 0, 100, datetime.now() + timedelta(minutes=2)),
                Waypoint(0, 0, 200, datetime.now() + timedelta(minutes=4))
            ],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=5)
        )

        drones = [
            Drone(
                id="sim1",
                waypoints=[
                    Waypoint(100, 0, 50, datetime.now() + timedelta(minutes=1)),
                    Waypoint(100, 0, 150, datetime.now() + timedelta(minutes=3))
                ],
                start_time=datetime.now() + timedelta(minutes=1),
                end_time=datetime.now() + timedelta(minutes=4)
            ),
            Drone(
                id="sim2",
                waypoints=[
                    Waypoint(0, 100, 100, datetime.now() + timedelta(minutes=1.5)),
                    Waypoint(0, 100, 200, datetime.now() + timedelta(minutes=3.5))
                ],
                start_time=datetime.now() + timedelta(minutes=1.5),
                end_time=datetime.now() + timedelta(minutes=4.5)
            )
        ]
        
        self.create_scenario("Scenario7_VerticalStacking", primary_drone, drones)
        
        # Scenario 8: Complex 3D Maneuvers
        print("\n=== Scenario 8: Complex 3D Maneuvers ===")
        primary_drone = Drone(
            id="primary",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now()),
                Waypoint(100, 0, 50, datetime.now() + timedelta(minutes=1)),
                Waypoint(100, 100, 100, datetime.now() + timedelta(minutes=2)),
                Waypoint(0, 100, 50, datetime.now() + timedelta(minutes=3)),
                Waypoint(0, 0, 150, datetime.now() + timedelta(minutes=4))
            ],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=5)
        )

        drones = [
            Drone(
                id="sim1",
                waypoints=[
                    Waypoint(50, 50, 25, datetime.now() + timedelta(minutes=0.5)),
                    Waypoint(150, 50, 75, datetime.now() + timedelta(minutes=1.5)),
                    Waypoint(150, 150, 125, datetime.now() + timedelta(minutes=2.5)),
                    Waypoint(50, 150, 75, datetime.now() + timedelta(minutes=3.5)),
                    Waypoint(50, 50, 125, datetime.now() + timedelta(minutes=4.5))
                ],
                start_time=datetime.now() + timedelta(minutes=0.5),
                end_time=datetime.now() + timedelta(minutes=6)
            )
        ]
        
        self.create_scenario("Scenario8_Complex3DManeuvers", primary_drone, drones)
        
        print("\nDemonstration complete! Check the 'demonstration_output' directory for visualizations.")
        print("Generated files:")
        print("- Static 3D visualizations (.png)")
        print("- Animated visualizations (.gif)")
        print("- Conflict explanations in terminal")

if __name__ == "__main__":
    demonstration = UAVDemonstration()
    demonstration.run_demonstration()
