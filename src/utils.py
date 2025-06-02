import logging
from functools import wraps
from time import time

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """Setup logger with optional file output"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_performance_metrics(func):
    """Decorator to log function execution time and memory usage"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        
        # Get function name and module
        func_name = func.__name__
        module_name = func.__module__.split('.')[-1]
        
        # Log performance metrics
        logger = logging.getLogger(f'{module_name}.{func_name}')
        logger.info(f"Execution time: {end_time - start_time:.4f} seconds")
        
        return result
    return wrapper

def get_logger(name: str):
    """Get or create a logger instance"""
    return logging.getLogger(name)

def validate_coordinates(x: float, y: float, z: float = 0) -> bool:
    """Validate that coordinates are within reasonable bounds"""
    # Define reasonable bounds for coordinates
    MAX_XY = 10000  # 10km
    MAX_Z = 500     # 500m altitude
    
    return (abs(x) <= MAX_XY and 
            abs(y) <= MAX_XY and 
            abs(z) <= MAX_Z)

def calculate_distance(p1: tuple, p2: tuple) -> float:
    """Calculate Euclidean distance between two points in 3D space"""
    return ((p1[0] - p2[0])**2 + 
            (p1[1] - p2[1])**2 + 
            (p1[2] - p2[2])**2)**0.5
