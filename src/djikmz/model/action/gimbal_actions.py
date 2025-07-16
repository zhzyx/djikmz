"""
Gimbal-related actions for DJI drones.
"""

from pydantic import Field, field_validator
from .action import Action, ActionType
from .registry import register_action


@register_action(ActionType.GIMBAL_ROTATE)
class GimbalRotateAction(Action):
    """Gimbal rotation action."""
    
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    gimbal_rotate_mode: str = Field(
        default='absoluteAngle',
        serialization_alias="gimbalRotateMode",
        description="from dji offical doc: absoluteAngle:The angle relative to the North."
    )
    @field_validator("gimbal_rotate_mode")
    @classmethod
    def validate_gimbal_rotate_mode(cls, v: str) -> str:
        if v != "absoluteAngle":
            raise ValueError("Invalid gimbal rotate mode, must be 'absoluteAngle'")
        return v
    gimbal_pitch_rotate_enable: int = Field(
        default=0,
        serialization_alias="gimbalPitchRotateEnable",
        ge=0, le=1,
        description="Enable pitch rotation (0: No, 1: Yes)"
    )
    gimbal_pitch_rotate_angle: float = Field(
        default=0.0,
        serialization_alias="gimbalPitchRotateAngle",
        description="Pitch rotation angle in degrees. Different gimbals can be turned in different ranges."
    )
    gimbal_roll_rotate_enable: int = Field(
        default=0,
        serialization_alias="gimbalRollRotateEnable", 
        ge=0, le=1,
        description="Enable roll rotation (0: No, 1: Yes)"
    )
    gimbal_roll_rotate_angle: float = Field(
        default=0.0,
        serialization_alias="gimbalRollRotateAngle",
        description="Roll rotation angle in degrees. Different gimbals can be turned in different ranges."
    )
    gimbal_yaw_rotate_enable: int = Field(
        default=0,
        serialization_alias="gimbalYawRotateEnable",
        ge=0, le=1,
        description="Enable yaw rotation (0: No, 1: Yes)"
    )
    gimbal_yaw_rotate_angle: float = Field(
        default=0.0,
        serialization_alias="gimbalYawRotateAngle",
        description="Yaw rotation angle in degrees. Different gimbals can be turned in different ranges."
    )
    gimbal_rotate_time_enable: int = Field(
        default=0,
        serialization_alias="gimbalRotateTimeEnable",
        ge=0, le=1,
        description="Enable rotation time limit (0: No, 1: Yes)"
    )
    gimbal_rotate_time: float = Field(
        default=0.0,
        serialization_alias="gimbalRotateTime",
        description="Rotation time in seconds"
    )
    heading_base: str = Field(
        default="north",
        serialization_alias="gimbalHeadingYawBase",
        description="from dji offical doc: north: Relative geographic north.",        
    )
    @field_validator("heading_base")
    @classmethod
    def validate_heading_base(cls, v: str) -> str:
        if v != "north":
            raise ValueError("Invalid gimbal heading yaw base, must be 'north'")
        return v


@register_action(ActionType.GIMBAL_EVENLY_ROTATE)
class GimbalEvenlyRotateAction(Action):
    """Gimbal evenly rotate action for smooth camera movements.
    Note: "gimbalEvenlyRotate" rotates the pitch angle of gimbal evenly 
        during the segments of the flight route. 
        The trigger must be "betweenAdjacentPoints".
        from the dji offical doc, it only provide the pitch angle element.
    """
    
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    pitch_rotate_angle: float = Field(
        default=0.0,
        serialization_alias="gimbalPitchRotateAngle",
        description="Pitch rotation angle in degrees. Different gimbals can be turned in different ranges."
    )