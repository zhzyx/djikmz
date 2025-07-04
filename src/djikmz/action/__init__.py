"""
DJI KMZ Action classes.

This module provides all the action classes for creating DJI drone missions.
Each action corresponds to a specific drone operation that can be performed
at waypoints during mission execution.

Available Actions:
- TakePhotoAction: Take a photo
- StartRecordAction: Start video recording  
- StopRecordAction: Stop video recording
- GimbalRotateAction: Rotate gimbal to specific angles
- GimbalEvenlyRotateAction: Smooth gimbal rotation over time
- HoverAction: Hover in place for specified time
- RotateYawAction: Rotate aircraft yaw to specific heading
- FocusAction: Set camera focus point or area
- ZoomAction: Set camera zoom level
- AccurateShootAction: Legacy accurate shooting (use OrientedShootAction)
- OrientedShootAction: Advanced oriented shooting with gimbal/aircraft control

Usage:
    from old_kmz.action import TakePhotoAction, HoverAction
    
    # Create actions
    photo = TakePhotoAction(action_id=1, file_suffix="waypoint1")
    hover = HoverAction(action_id=2, hover_time=10.0)
"""

# Import the base classes
from .action import Action, ActionType
from .registry import register_action, ACTION_REGISTRY

# Import all action implementations
from .record_actions import StartRecordAction, StopRecordAction
from .gimbal_actions import GimbalRotateAction, GimbalEvenlyRotateAction
from .movement_actions import HoverAction, RotateYawAction
from .camera_actions import (
    TakePhotoAction,
    FocusAction, 
    ZoomAction, 
    AccurateShootAction, 
    OrientedShootAction
)

# Export all action classes
__all__ = [
    # Base classes
    'Action',
    'ActionType', 
    'register_action',
    'ACTION_REGISTRY',
    
    # Action implementations
    'TakePhotoAction',
    'StartRecordAction',
    'StopRecordAction', 
    'GimbalRotateAction',
    'GimbalEvenlyRotateAction',
    'HoverAction',
    'RotateYawAction',
    'FocusAction',
    'ZoomAction',
    'AccurateShootAction',
    'OrientedShootAction',
]