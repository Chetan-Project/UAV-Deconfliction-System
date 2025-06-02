# UAV Strategic Deconfliction System

A strategic deconfliction system for verifying UAV flight paths in shared airspace. The system checks for conflicts in both space and time against simulated flight paths of multiple drones using advanced 4D analysis.

## Features

- 4D (3D space + time) conflict detection with safety buffer
- Efficient spatial and temporal validation using KDTree and temporal indexing
- Real-time visualization of drone trajectories
- Detailed conflict explanation and resolution
- Scalable architecture with caching
- Performance benchmarking
- Automated testing suite

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Demonstration

Run the demo to see the system in action:
```bash
python demonstration.py
```

This will generate visualizations in the `demonstration_output` directory and create a demonstration video.

### Running Tests

Run the test suite:
```bash
python -m pytest tests/
```

Run performance benchmark:
```bash
python tests/performance_test.py
```

## Project Structure

```
UAV_Deconfliction/
├── src/
│   ├── drone.py          # Drone and waypoint data structures
│   ├── deconfliction.py  # Core deconfliction logic
│   ├── visualization.py   # Visualization components
│   ├── conflict.py       # Conflict point representation
│   └── utils.py          # Utility functions and logging
├── tests/
│   ├── test_deconfliction.py  # Unit tests
│   └── performance_test.py    # Performance benchmark
├── demonstration.py      # Demonstration script
├── video_generator.py    # Video generation script
├── requirements.txt      # Project dependencies
├── README.md            # Documentation
└── voiceover.txt        # Demonstration video narration
```

## Requirements

- Python 3.8+
- Required packages (listed in requirements.txt):
  - numpy
  - matplotlib
  - scipy
  - opencv-python
  - pillow
  - pytest

## Performance

The system demonstrates linear scaling with number of drones:
- Execution time: O(n) where n is number of drones
- Cache size: O(n²) for drone pairs
- Efficient spatial indexing using KDTree
- Temporal indexing for time-based conflicts

## License

MIT License

## Acknowledgments

Created by Chetan Tangale

For more information about the system architecture and design decisions, please refer to the Reflection Document.
