"""
DjiKMZ - DJI Task Plan KMZ File Generator

A Python package for generating DJI task plan KMZ files with comprehensive 
type safety, validation, and integrity checks.

Basic Usage:
    from djikmz import DroneTask
    
    mission = DroneTask("M30T", "Pilot").fly_to(lat, lon).build()

Advanced Usage:
    from djikmz.model import KML, Waypoint, DroneModel
    # For deep customization and direct model access
"""

from .task_builder import DroneTask, ValidationError, HardwareError

__version__ = "0.1.0"
__all__ = [
    "DroneTask",
    "ValidationError", 
    "HardwareError",
]