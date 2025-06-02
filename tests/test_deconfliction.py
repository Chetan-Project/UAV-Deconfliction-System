import unittest
from datetime import datetime, timedelta
from src.drone import Drone, Waypoint
from src.deconfliction import DeconflictionSystem

class TestDeconflictionSystem(unittest.TestCase):
    def setUp(self):
        self.system = DeconflictionSystem(safety_buffer=10.0)

    def test_no_conflict(self):
        """Test mission with no conflicts"""
        drone = Drone(
            id="test",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now()),
                Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=5))
            ],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=10)
        )

        result = self.system.validate_mission(drone)
        self.assertEqual(result['status'], 'clear')
        self.assertEqual(len(result['conflicts']), 0)
        self.assertGreaterEqual(result['performance']['spatial_checks'], 0)
        self.assertGreaterEqual(result['performance']['temporal_checks'], 0)

    def test_spatial_conflict(self):
        """Test mission with spatial conflict"""
        drone1 = Drone(
            id="drone1",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now()),
                Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=5))
            ],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=10)
        )

        drone2 = Drone(
            id="drone2",
            waypoints=[
                Waypoint(50, 50, 25, datetime.now() + timedelta(minutes=2)),
                Waypoint(150, 150, 75, datetime.now() + timedelta(minutes=4))
            ],
            start_time=datetime.now() + timedelta(minutes=2),
            end_time=datetime.now() + timedelta(minutes=6)
        )

        self.system.add_simulated_drone(drone2)
        result = self.system.validate_mission(drone1)
        self.assertEqual(result['status'], 'conflict')
        self.assertGreater(len(result['conflicts']), 0)
        self.assertGreater(len(result['conflicts'][0]['conflict_locations']), 0)
        self.assertTrue(result['performance']['spatial_checks'] > 0)

    def test_temporal_conflict(self):
        """Test mission with temporal conflict"""
        drone1 = Drone(
            id="drone1",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now()),
                Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=5))
            ],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=10)
        )

        drone2 = Drone(
            id="drone2",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now() + timedelta(minutes=4)),
                Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=9))
            ],
            start_time=datetime.now() + timedelta(minutes=4),
            end_time=datetime.now() + timedelta(minutes=15)
        )

        self.system.add_simulated_drone(drone2)
        result = self.system.validate_mission(drone1)
        self.assertEqual(result['status'], 'conflict')
        self.assertGreater(len(result['conflicts']), 0)
        self.assertTrue(result['performance']['temporal_checks'] > 0)

    def test_full_conflict(self):
        """Test mission with both spatial and temporal conflicts"""
        drone1 = Drone(
            id="drone1",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now()),
                Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=5))
            ],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=10)
        )

        drone2 = Drone(
            id="drone2",
            waypoints=[
                Waypoint(10, 10, 10, datetime.now() + timedelta(minutes=1)),
                Waypoint(90, 90, 40, datetime.now() + timedelta(minutes=4))
            ],
            start_time=datetime.now() + timedelta(minutes=1),
            end_time=datetime.now() + timedelta(minutes=9)
        )

        self.system.add_simulated_drone(drone2)
        result = self.system.validate_mission(drone1)
        self.assertEqual(result['status'], 'conflict')
        self.assertGreater(len(result['conflicts']), 0)
        self.assertTrue(result['performance']['spatial_checks'] > 0)
        self.assertTrue(result['performance']['temporal_checks'] > 0)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test zero distance waypoints
        drone1 = Drone(
            id="drone1",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now()),
                Waypoint(0, 0, 0, datetime.now() + timedelta(minutes=5))
            ],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=10)
        )

        drone2 = Drone(
            id="drone2",
            waypoints=[
                Waypoint(0, 0, 0, datetime.now() + timedelta(minutes=2)),
                Waypoint(0, 0, 0, datetime.now() + timedelta(minutes=7))
            ],
            start_time=datetime.now() + timedelta(minutes=2),
            end_time=datetime.now() + timedelta(minutes=15)
        )

        self.system.add_simulated_drone(drone2)
        result = self.system.validate_mission(drone1)
        self.assertEqual(result['status'], 'conflict')
        
        # Test maximum drone limit
        max_drones = 1000
        system = DeconflictionSystem(max_simulated_drones=max_drones)
        
        for i in range(max_drones):
            drone = Drone(
                id=f"drone_{i}",
                waypoints=[
                    Waypoint(i*10, i*10, i*10, datetime.now() + timedelta(minutes=i)),
                    Waypoint((i+1)*10, (i+1)*10, (i+1)*10, datetime.now() + timedelta(minutes=i+5))
                ],
                start_time=datetime.now() + timedelta(minutes=i),
                end_time=datetime.now() + timedelta(minutes=i+10)
            )
            system.add_simulated_drone(drone)

        # Test adding one more drone should fail
        with self.assertRaises(ValueError):
            drone = Drone(
                id="extra_drone",
                waypoints=[
                    Waypoint(0, 0, 0, datetime.now()),
                    Waypoint(100, 100, 50, datetime.now() + timedelta(minutes=5))
                ],
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(minutes=10)
            )
            system.add_simulated_drone(drone)

    def test_performance(self):
        """Test system performance with large dataset"""
        system = DeconflictionSystem()
        
        # Add 1000 drones with random trajectories
        import random
        num_drones = 1000
        for i in range(num_drones):
            drone = Drone(
                id=f"drone_{i}",
                waypoints=[
                    Waypoint(random.uniform(0, 1000), random.uniform(0, 1000), random.uniform(0, 100), 
                            datetime.now() + timedelta(minutes=i)),
                    Waypoint(random.uniform(0, 1000), random.uniform(0, 1000), random.uniform(0, 100), 
                            datetime.now() + timedelta(minutes=i+5))
                ],
                start_time=datetime.now() + timedelta(minutes=i),
                end_time=datetime.now() + timedelta(minutes=i+10)
            )
            system.add_simulated_drone(drone)

        # Validate a new mission
        primary_drone = Drone(
            id="primary",
            waypoints=[
                Waypoint(500, 500, 50, datetime.now() + timedelta(minutes=10)),
                Waypoint(600, 600, 60, datetime.now() + timedelta(minutes=15))
            ],
            start_time=datetime.now() + timedelta(minutes=10),
            end_time=datetime.now() + timedelta(minutes=20)
        )

        result = system.validate_mission(primary_drone)
        self.assertIn(result['status'], ['clear', 'conflict'])
        self.assertGreater(result['performance']['spatial_checks'], 0)
        self.assertGreater(result['performance']['temporal_checks'], 0)

if __name__ == '__main__':
    unittest.main()
