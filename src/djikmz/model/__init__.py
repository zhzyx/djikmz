"""
DjiKMZ Model Components

This module provides direct access to all DJI KMZ data models for advanced 
customization and integration. Most users should use the DroneTask API instead.

Examples:
    # Direct model usage
    from djikmz.model import KML, Waypoint, DroneModel
    from djikmz.model.action import TakePhotoAction
    
    # Create models directly
    waypoint = Waypoint(lat=37.7749, lon=-122.4194)
    action = TakePhotoAction(action_id=1)
"""

# Core models
from .kml import KML
from .waypoint import Waypoint, Point
from .mission_config import (
    MissionConfig, 
    DroneModel, 
    PayloadModel,
    DroneInfo,
    PayloadInfo
)
from .action_group import ActionGroup, ActionTrigger, TriggerType

# Parameter models
from .coordinate_system_param import CoordinateSystemParam
from .heading_param import WaypointHeadingParam, WaypointPoiPoint  
from .turn_param import WaypointTurnParam

# Action models - import from action subpackage
from .action import *

__all__ = [
    # Core models
    "KML",
    "Waypoint", 
    "Point",
    "MissionConfig",
    "DroneModel",
    "PayloadModel", 
    "DroneInfo",
    "PayloadInfo",
    "ActionGroup",
    "ActionTrigger",
    "TriggerType",
    
    # Parameter models
    "CoordinateSystemParam",
    "WaypointHeadingParam",
    "WaypointPoiPoint",
    "WaypointTurnParam",
    
    # Actions (from action subpackage)
    # These will be available as djikmz.model.TakePhotoAction etc.
]