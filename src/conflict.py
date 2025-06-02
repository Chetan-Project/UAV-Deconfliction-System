from dataclasses import dataclass
from typing import Tuple

@dataclass
class ConflictPoint:
    """Represents a point of conflict between drones"""
    drone_id: str
    point: Tuple[float, float, float]
    type: str  # "spatial" or "temporal"
    severity: str  # "low", "medium", "high"
    
    def __str__(self):
        return (f"Conflict with drone {self.drone_id} at {self.point}"
                f" ({self.type} conflict, severity: {self.severity})")
