from typing import List, Dict, Tuple
from datetime import datetime
import numpy as np
from scipy.spatial import KDTree
from .drone import Drone, Waypoint
from .conflict import ConflictPoint
from .utils import get_logger, log_performance_metrics

class DeconflictionSystem:
    def __init__(self, safety_buffer: float = 10.0, max_simulated_drones: int = 1000):
        """
        Initialize the deconfliction system
        
        Args:
            safety_buffer: Minimum distance in meters to maintain between drones
            max_simulated_drones: Maximum number of simulated drones to track
        """
        self.logger = get_logger(__name__)
        self.safety_buffer = safety_buffer
        self.max_simulated_drones = max_simulated_drones
        self.simulated_drones: Dict[str, Drone] = {}
        self.spatial_index: Optional[KDTree] = None
        self.time_index: Dict[datetime, List[str]] = {}
        self.conflict_cache: Dict[str, List[Tuple[float, float, float]]] = {}
        self.logger.info(f"Initialized DeconflictionSystem with safety buffer: {safety_buffer}m")

    @log_performance_metrics
    def add_simulated_drone(self, drone: Drone):
        """
        Add a simulated drone to the system
        
        Args:
            drone: Drone object to add
            
        Raises:
            ValueError: If maximum number of drones is exceeded
        """
        if len(self.simulated_drones) >= self.max_simulated_drones:
            self.logger.error(f"Maximum number of drones ({self.max_simulated_drones}) exceeded")
            raise ValueError(f"Maximum number of drones ({self.max_simulated_drones}) exceeded")
        
        self.simulated_drones[drone.id] = drone
        self._update_indexes(drone)
        self.logger.info(f"Added simulated drone {drone.id} with {len(drone.waypoints)} waypoints")

    @log_performance_metrics
    def validate_mission(self, primary_drone: Drone) -> Dict:
        """
        Validate the primary drone's mission against all simulated drones
        Returns a dictionary with validation results and conflict details
        """
        self.logger.info(f"Validating mission for drone {primary_drone.id}")
        
        results = {
            'status': 'clear',
            'conflicts': [],
            'performance': {
                'spatial_checks': 0,
                'temporal_checks': 0,
                'cache_hits': 0,
                'total_drones': len(self.simulated_drones),
                'validation_time': None
            }
        }

        start_time = datetime.now()
        
        # First check time-based index to reduce number of spatial checks
        relevant_drones = []
        start_time, end_time = primary_drone.get_time_range()
        
        # Find drones that could potentially conflict based on time
        for time in self.time_index:
            if start_time <= time <= end_time:
                relevant_drones.extend(self.time_index[time])

        relevant_drones = list(set(relevant_drones))
        self.logger.debug(f"Found {len(relevant_drones)} potentially conflicting drones")

        for drone_id in relevant_drones:
            simulated_drone = self.simulated_drones[drone_id]
            results['performance']['temporal_checks'] += 1

            if self._check_temporal_conflict(primary_drone, simulated_drone):
                results['performance']['spatial_checks'] += 1
                spatial_conflicts = self._check_spatial_conflict(primary_drone, simulated_drone)
                if spatial_conflicts:
                    results['status'] = 'conflict'
                    results['conflicts'].append({
                        'conflicting_drone': drone_id,
                        'conflict_locations': spatial_conflicts,
                        'time_overlap': {
                            'start': max(primary_drone.start_time, simulated_drone.start_time),
                            'end': min(primary_drone.end_time, simulated_drone.end_time)
                        }
                    })

        results['performance']['validation_time'] = str(datetime.now() - start_time)
        return results

    def _update_indexes(self, drone: Drone):
        """
        Update spatial and temporal indexes when a drone is added
        """
        # Update spatial index
        if self.spatial_index is None:
            points = [(wp.x, wp.y, wp.z) for wp in drone.waypoints]
            self.spatial_index = KDTree(points)
        else:
            points = self.spatial_index.data.tolist()
            points.extend([(wp.x, wp.y, wp.z) for wp in drone.waypoints])
            self.spatial_index = KDTree(points)

        # Update time index
        start_time, end_time = drone.get_time_range()
        for time in [start_time, end_time]:
            if time not in self.time_index:
                self.time_index[time] = []
            self.time_index[time].append(drone.id)

    def _check_point_conflict(self, wp1: Waypoint, wp2: Waypoint) -> bool:
        """
        Check if two waypoints are in conflict based on safety buffer.
        
        Args:
            wp1 (Waypoint): First waypoint
            wp2 (Waypoint): Second waypoint
            
        Returns:
            bool: True if waypoints are in conflict, False otherwise
            
        Performance:
            Time Complexity: O(1)
            Space Complexity: O(1)
        """
        # Calculate 3D distance between waypoints
        dx = wp1.x - wp2.x
        dy = wp1.y - wp2.y
        dz = wp1.z - wp2.z
        distance = (dx**2 + dy**2 + dz**2) ** 0.5
        
        # Check if distance is less than safety buffer
        return distance < self.safety_buffer

    def _check_spatial_conflict(self, primary_drone: Drone, simulated_drone: Drone) -> List[ConflictPoint]:
        """
        Check for spatial conflicts with other drones in 3D space.
        
        Args:
            primary_drone (Drone): The drone to check for conflicts
            simulated_drone (Drone): The drone to check against
            
        Returns:
            List[ConflictPoint]: List of spatial conflict points
            
        Performance:
            Time Complexity: O(n * m) where n is number of waypoints and m is number of drones
            Space Complexity: O(1) additional space
        """
        # Get cached results if available
        cache_key = f"spatial_{primary_drone.id}_{simulated_drone.id}"
        if cache_key in self.conflict_cache:
            return self.conflict_cache[cache_key]
        
        conflicts = []
        for wp1 in primary_drone.waypoints:
            for wp2 in simulated_drone.waypoints:
                if self._check_point_conflict(wp1, wp2):
                    conflicts.append(ConflictPoint(
                        drone_id=simulated_drone.id,
                        point=(wp1.x, wp1.y, wp1.z),
                        type="spatial",
                        severity="high"
                    ))
        
        # Cache results
        self.conflict_cache[cache_key] = conflicts
        return conflicts

    def _check_temporal_conflict(self, primary_drone: Drone, simulated_drone: Drone) -> bool:
        """
        Check for temporal conflicts with other drones.
        
        Args:
            primary_drone (Drone): The drone to check for conflicts
            simulated_drone (Drone): The drone to check against
            
        Returns:
            bool: True if temporal conflict exists, False otherwise
            
        Performance:
            Time Complexity: O(1)
            Space Complexity: O(1)
        """
        # Get cached results if available
        cache_key = f"temporal_{primary_drone.id}_{simulated_drone.id}"
        if cache_key in self.conflict_cache:
            return self.conflict_cache[cache_key]
        
        # Check if any drone occupies the same space at different times
        t1_start, t1_end = primary_drone.get_time_range()
        t2_start, t2_end = simulated_drone.get_time_range()
        
        # Check if time ranges overlap
        conflict = not (t1_end <= t2_start or t1_start >= t2_end)
        
        # Cache results
        self.conflict_cache[cache_key] = conflict
        return conflict

    def get_conflict_explanation(self, validation_results: Dict) -> str:
        """
        Generate a human-readable explanation of conflicts
        
        Performance:
            Time Complexity: O(n) where n is number of conflicts
            Space Complexity: O(n) additional space
        """
        if validation_results['status'] == 'clear':
            return "No conflicts detected in the mission."
        
        explanation = []
        for conflict in validation_results['conflicts']:
            drone_id = conflict['conflicting_drone']
            time_overlap = conflict['time_overlap']
            locations = conflict['conflict_locations']
            
            explanation.append(f"\nConflict with drone {drone_id}:")
            explanation.append(f"Time overlap: {time_overlap['start']} to {time_overlap['end']}")
            explanation.append(f"Number of conflict locations: {len(locations)}")
            explanation.append("Locations:")
            for loc in locations[:5]:  # Show first 5 locations
                explanation.append(f"  - X: {loc[0]:.2f}, Y: {loc[1]:.2f}, Z: {loc[2]:.2f}")
            
            if len(locations) > 5:
                explanation.append(f"  ... and {len(locations)-5} more locations")
        
        return "\n".join(explanation)
