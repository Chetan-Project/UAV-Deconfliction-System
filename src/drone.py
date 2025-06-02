from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
from datetime import datetime
from .utils import get_logger, validate_coordinates, calculate_distance

class Waypoint:
    def __init__(self, x: float, y: float, z: float = 0, timestamp: datetime = None):
        """
        Represents a waypoint in 3D space with optional timestamp
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate (altitude, optional)
            timestamp: Time when the drone should reach this waypoint
        """
        self.x = x
        self.y = y
        self.z = z
        self.timestamp = timestamp if timestamp else datetime.now()
    
    def distance_to(self, other: 'Waypoint') -> float:
        """
        Calculate Euclidean distance to another waypoint
        
        Args:
            other: Another Waypoint object
            
        Returns:
            float: Distance between waypoints
        """
        return np.sqrt((self.x - other.x)**2 + 
                      (self.y - other.y)**2 + 
                      (self.z - other.z)**2)
    
    def __repr__(self):
        return f"Waypoint(x={self.x}, y={self.y}, z={self.z}, time={self.timestamp})"

@dataclass
class Drone:
    id: str
    waypoints: List[Waypoint]
    start_time: datetime
    end_time: datetime
    safety_buffer: float = 10.0  # meters
    
    def __init__(self, id: str, waypoints: List[Waypoint], start_time: datetime, end_time: datetime):
        self.id = id
        self.waypoints = waypoints
        self.start_time = start_time
        self.end_time = end_time
        self.logger = get_logger(f"drone.{self.id}")
    
    def __post_init__(self):
        """Validate initialization parameters"""
        if not self.waypoints:
            raise ValueError("A drone must have at least one waypoint")
        
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        
        # Validate all waypoint coordinates
        for waypoint in self.waypoints:
            if not validate_coordinates(waypoint.x, waypoint.y, waypoint.z):
                raise ValueError(f"Invalid coordinates for waypoint: ({waypoint.x}, {waypoint.y}, {waypoint.z})")
    
    def get_trajectory(self) -> List[Tuple[float, float, float]]:
        """Get the 3D trajectory of the drone"""
        return [(wp.x, wp.y, wp.z) for wp in self.waypoints]
    
    def get_time_range(self) -> Tuple[datetime, datetime]:
        """Get the time range of the drone's mission"""
        return self.start_time, self.end_time
    
    def get_speed(self) -> float:
        """
        Calculate average speed of the drone
        
        Returns:
            float: Average speed in meters per second
        """
        total_distance = sum(self.waypoints[i].distance_to(self.waypoints[i+1]) 
                           for i in range(len(self.waypoints)-1))
        total_time = (self.end_time - self.start_time).total_seconds()
        return total_distance / total_time if total_time > 0 else 0
    
    def validate_trajectory(self) -> bool:
        """
        Validate that the drone's trajectory is valid
        
        Returns:
            bool: True if trajectory is valid, False otherwise
        """
        # Check that waypoints are in chronological order
        for i in range(len(self.waypoints) - 1):
            if self.waypoints[i].timestamp > self.waypoints[i+1].timestamp:
                return False
        
        # Check that total time matches start and end times
        total_time = (self.end_time - self.start_time).total_seconds()
        if total_time <= 0:
            return False
        
        return True
