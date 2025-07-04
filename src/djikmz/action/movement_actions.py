"""
Movement and positioning actions for DJI drones.
"""

from pydantic import Field
from .action import Action, ActionType
from .registry import register_action
from pydantic import field_validator


@register_action(ActionType.HOVER)
class HoverAction(Action):
    """Hover action to make the drone stay in place for a specified time."""
    
    hover_time: float = Field(
        default=1,
        serialization_alias="hoverTime",
        description="Hover time in seconds, dji offical doc says float, but in reality it is an integer",
        gt=0.0
    )


@register_action(ActionType.ROTATE_YAW)
class RotateYawAction(Action):
    """Rotate aircraft yaw action."""
    
    aircraft_heading: float = Field(
        default=0.0,
        serialization_alias="aircraftHeading",
        ge=-180.0, le=180.0,
        description="Target aircraft heading in degrees. azimuth angle, 0 is north, 90 is east"
    )
    direction: str = Field(
        default='clockwise',
        serialization_alias="aircraftPathMode",
        description="clockwise or counterClockwise"
    )
    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v: str) -> str:
        if v not in ['clockwise', 'counterClockwise']:
            raise ValueError("Invalid direction, must be 'clockwise' or 'counterClockwise'")
        return v
