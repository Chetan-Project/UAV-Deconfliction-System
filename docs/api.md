# API Documentation

## Core Classes

### Drone
```python
class Drone:
    def __init__(self, id: str, waypoints: List[Waypoint], start_time: datetime, end_time: datetime)
    
    # Properties
    id: str
    waypoints: List[Waypoint]
    start_time: datetime
    end_time: datetime
    
    # Methods
    def get_current_position(self, timestamp: datetime) -> Tuple[float, float, float]
    def get_next_waypoint(self, timestamp: datetime) -> Waypoint
    def get_mission_duration(self) -> timedelta
```

### DeconflictionSystem
```python
class DeconflictionSystem:
    def __init__(self, safety_buffer: float = 10.0, temporal_buffer: timedelta = timedelta(minutes=15))
    
    # Properties
    safety_buffer: float
    temporal_buffer: timedelta
    
    # Methods
    def add_simulated_drone(self, drone: Drone) -> None
    def validate_mission(self, primary_drone: Drone) -> Dict[str, Any]
    def get_conflict_points(self, drone1: Drone, drone2: Drone) -> List[ConflictPoint]
    def clear_cache(self) -> None
```

### Waypoint
```python
class Waypoint:
    def __init__(self, x: float, y: float, z: float, timestamp: datetime)
    
    # Properties
    x: float
    y: float
    z: float
    timestamp: datetime
```

## Key Methods

### Mission Validation
```python
# Validate a new mission against existing drones
def validate_mission(self, primary_drone: Drone) -> Dict[str, Any]:
    """
    Validate a new mission against existing drones for conflicts.
    
    Args:
        primary_drone: The drone to validate
        
    Returns:
        Dict containing validation results:
        {
            "spatial_conflicts": List[ConflictPoint],
            "temporal_conflicts": List[Tuple[Drone, Drone]],
            "is_valid": bool
        }
    """
```

### Conflict Detection
```python
# Check for conflicts between two drones
def get_conflict_points(self, drone1: Drone, drone2: Drone) -> List[ConflictPoint]:
    """
    Get potential conflict points between two drones.
    
    Args:
        drone1: First drone
        drone2: Second drone
        
    Returns:
        List of ConflictPoint objects where conflicts may occur
    """
```

## Usage Example
```python
# Create a deconfliction system
system = DeconflictionSystem()

# Add simulated drones
for drone_data in drone_data_list:
    drone = Drone(**drone_data)
    system.add_simulated_drone(drone)

# Validate a new mission
new_drone = Drone(...)
validation_result = system.validate_mission(new_drone)

if validation_result["is_valid"]:
    print("Mission is valid")
else:
    print("Conflicts found:")
    print(f"Spatial conflicts: {len(validation_result['spatial_conflicts'])}")
    print(f"Temporal conflicts: {len(validation_result['temporal_conflicts'])}")
```

## Error Handling

### Common Exceptions
- `InvalidMissionException`: Raised for invalid mission parameters
- `ConflictException`: Raised when conflicts are detected
- `SystemException`: Raised for system-level errors

### Example Error Handling
```python
try:
    validation_result = system.validate_mission(drone)
except InvalidMissionException as e:
    print(f"Invalid mission: {e}")
except ConflictException as e:
    print(f"Conflicts detected: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
