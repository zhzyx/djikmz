"""
Record-related actions for DJI drones.
"""

from pydantic import Field
from .action import Action, ActionType
from .registry import register_action
from .camera_actions import PAYLOAD_LENS


@register_action(ActionType.START_RECORD)
class StartRecordAction(Action):
    """Start recording action."""
    
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    payload_lens: PAYLOAD_LENS|str|None = Field(
        default=None,
        serialization_alias="payloadLens",
        description="Payload lens index."
    )
    file_suffix: str|None = Field(
        default=None,
        serialization_alias="fileSuffix",
        description="Suffix for the recorded file name"
    )
    use_global_payload_lens_index: int = Field(
        default=0,
        serialization_alias="useGlobalPayloadLensIndex",
        description="Use global payload lens index (0: No, 1: Yes)" ,
        ge=0, le=1
    )

@register_action(ActionType.STOP_RECORD)
class StopRecordAction(Action):
    """Stop recording action."""
    
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    payload_lens: PAYLOAD_LENS|str|None = Field(
        default=None,
        serialization_alias="payloadLens",
        description="Payload lens index."
    )