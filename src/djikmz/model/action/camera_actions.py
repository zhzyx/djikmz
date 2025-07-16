"""
Camera control actions for DJI drones.
"""

from pydantic import Field, field_validator
from .action import Action, ActionType
from .registry import register_action
from enum import Enum

class PAYLOAD_LENS(str, Enum):
    """Enum for payload lens index."""
    def __str__(self):
        return self.value
    ZOOM = "zoom"
    WIDE = "wide"
    IR = "ir"
    NARROW_BAND = "narrow_band"
    VISABLE = "visable"
    
def validate_payload_lens(value: PAYLOAD_LENS|str|None) -> PAYLOAD_LENS|None:
    """Validate payload lens index."""
    if value is None:
        return None
    if isinstance(value, PAYLOAD_LENS):
        return value
    if isinstance(value, str):
        return PAYLOAD_LENS(value)
    raise TypeError(f"payload_lens must be PAYLOAD_LENS or str, got {type(value)}")


@register_action(ActionType.TAKE_PHOTO)
class TakePhotoAction(Action):
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    file_suffix: str = Field(
        default='',
        serialization_alias="fileSuffix",
        description="Suffix for the photo file name"
    )
    payload_lens: PAYLOAD_LENS|str|None = Field(
        default=None,
        serialization_alias="payloadLensIndex",
        description="Payload lens index (None for default, or specific lens index)"
    )
    use_global_payload_lens_index: int = Field(
        default=0,
        serialization_alias="useGlobalPayloadLensIndex",
        description="Use global payload lens index (0: No, 1: Yes)" ,
        ge=0, le=1
    )
    
    @field_validator('payload_lens')
    @classmethod
    def validate_payload_lens_field(cls, v):
        return validate_payload_lens(v)


@register_action(ActionType.FOCUS)
class FocusAction(Action):
    """Focus action for camera control."""
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    is_point_focus: int = Field(
        default=0,
        serialization_alias="isPointFocus",
        ge=0, le=1,
        description="Focus type (0: Area focus, 1: Point focus)"
    )
    focus_x: float = Field(
        default=0.4,
        serialization_alias="focusX",
        ge=0.0, le=1.0,
        description="Focus area upper left X coordinate (0.0 = left, 1.0 = right)"
    )
    focus_y: float = Field(
        default=0.4,
        serialization_alias="focusY",
        ge=0.0, le=1.0,
        description="Focus area upper left Y coordinate (0.0 = top, 1.0 = bottom)"
    )
    focus_region_width: float = Field(
        default=0.2,
        serialization_alias="focusRegionWidth",
        ge=0.0, le=1.0,
        description="Focus region width ratio to the image (0.0 = no width, 1.0 = full width)"
    )
    focus_region_height: float = Field(
        default=0.2,
        serialization_alias="focusRegionHeight",
        ge=0.0, le=1.0,
        description="Focus region height ratio to the image (0.0 = no height, 1.0 = full height)"
    )
    is_infinite_focus: int = Field(
        default=0,
        serialization_alias="isInfiniteFocus",
        ge=0, le=1,
        description="Use infinite focus (0: No, 1: Yes)"
    )


@register_action(ActionType.ZOOM)
class ZoomAction(Action):
    """Zoom action for camera control."""
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    focal_length: float = Field(
        default=24.0,
        serialization_alias="focalLength",
        ge=24.0, le=240.0,
        description="Target focal length in mm"
    )


@register_action(ActionType.ACCURATE_SHOOT)
class AccurateShootAction(Action):
    """Accurate shoot action (legacy, use OrientedShootAction instead)."""
    gimbal_pitch: float = Field(
        default=0.0,
        serialization_alias="gimbalPitchRotateAngle",
        description="Gimbal pitch angle for shooting",
        ge=-120.0, le=45.0
    )
    gimbal_yaw: float = Field(
        default=0.0,
        serialization_alias="gimbalYawRotateAngle",
        description="Gimbal yaw angle for shooting",
        ge=-180.0, le=180.0
    )
    focus_x: int = Field(
        default=960//2 - 20,
        serialization_alias="focusX",
        description="Focus area upper left X coordinate in px",
        ge=0, le=960
    )
    focus_y: int = Field(
        default=720//2 - 20,
        serialization_alias="focusY",
        description="Focus area upper left Y coordinate in px",
        ge=0, le=720
    )
    focus_width: int = Field(
        default=40,
        serialization_alias="focusRegionWidth",
        serialization_description="Focus region width in px",
        ge=0, le=960
    )
    focus_height: int = Field(
        default=40,
        serialization_alias="focusRegionHeight",
        serialization_description="Focus region height in px",
        ge=0, le=720
    )
    focal_length: float = Field(
        default=24.0,
        serialization_alias="focalLength",
        description="Target focal length in mm",
        ge=0.0
    )
    drone_heading: float = Field(
        default=0.0,
        serialization_alias="aircraftHeading",
        description="Drone heading in degrees, 0 for North",
        ge=-180.0, le=180.0
    )
    ai_spot_check: int = Field(
        default=0,
        serialization_alias="accurateFrameValid",
        description="totally no idea what this is from the dji docs:\
                    1: Selected  0: Not selected  Note: This value sets to 1. Then the drone will automatically find \" \
                    the target and capture photos. This value sets to 0. Then the drone will repeat action according to \
                    the drone attitude and payload attitude. It will not automatically find the target.",
        ge=0, le=1
    )
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    payload_lens: PAYLOAD_LENS|str|None = Field(
        default=None,
        serialization_alias="payloadLensIndex",
        description="Payload lens index (None for default, or specific lens index)"
    )
    use_global_payload_lens_index: int = Field(
        default=0,
        serialization_alias="useGlobalPayloadLensIndex",
        description="Use global payload lens index (0: No, 1: Yes)" ,
        ge=0, le=1
    )
    target_angle: float = Field(
        default=0.0,
        serialization_alias="targetAngle",
        description="totally no idea what this is from the dji docs:\
                    Angle of target box. Note: The rotation angle. (Based on the y-axis and rotate clockwise.",
        ge=0, le=360.0
    )
    image_width: int = Field(
        default=960,
        serialization_alias="imageWidth",
        description="wtf why put fixed value here?",
        ge=960, le=960
    )
    
    @field_validator('payload_lens')
    @classmethod  
    def validate_payload_lens_accurate(cls, v):
        return validate_payload_lens(v)
    image_height: int = Field(
        default=720,
        serialization_alias="imageHeight",
        description="wtf why put fixed value here?",
        ge=720, le=720
    )
    afpos: int|None = Field(
        default=None,
        serialization_alias="AFPos",
        description="dji even doesnt provide any description for this field. not sure default value is correct.",
    )
    gimbal_port: int = Field(
        default=0,
        serialization_alias="gimbalPort",
        description="from dji docs:\
                    Capturing camera installation position\
                    Note: This value of M30/M30T models are 0.",
        ge=0, le=0
    )
    camera_type: int = Field(
        default=52,
        serialization_alias="accurateCameraType",
        description="from dji docs:\
                    52 (Model: M30 dual light camera),\
                    53 (Model: M30T tripple light camera),\
                    42 (Model: H20),\
                    43 (Model: H20T),\
                    82 (Model: H30),\
                    83 (Model: H30T)",
        ge=0, le=100
    )
    file_path: str|None = Field(
        default=None,
        serialization_alias="accurateFilePath",
        description="no description from dji offical doc, doc says required field not sure if this is correct"
    )
    file_md5: str|None = Field(
        default=None,
        serialization_alias="accurateFileMD5",
        description="why the hell this is required field? dji offical doc says this is required field, but no description provided",
    )
    file_size: int|None = Field(
        default=None,
        serialization_alias="accurateFileSize",
        description="Speechless. dji offical doc says this is required field, real image file size in bytes",
    )
    file_suffix: str = Field(
        default='',
        serialization_alias="accurateFileSuffix",
        description="File suffix is added when the generated media files are named.",
    )
    apertue: int|None = Field(
        default=None,
        serialization_alias="accurateCameraApertue",
        description="Note: This value is the real aperture x 100"
    )
    luminance: int|None = Field(
        default=None,
        serialization_alias="accurateCameraLuminance",
        description="from dji offical doc: Environment luminance"
    )
    exposure_time: float|None = Field(
        default=None,
        serialization_alias="accurateCameraShutterTime",
        description="from dji offical doc: 	Shutter time in second. it probably means exposure time",
    )
    iso: int|None = Field(
        default=None,
        serialization_alias="accurateCameraISO",
        description="ISO"
    )


@register_action(ActionType.ORIENTED_SHOOT)
class OrientedShootAction(Action):
    """
    Oriented shoot action for advanced photo capture with AI Spot-Check capability.
    """
    """Accurate shoot action (legacy, use OrientedShootAction instead)."""
    gimbal_pitch: float = Field(
        default=0.0,
        serialization_alias="gimbalPitchRotateAngle",
        description="Gimbal pitch angle for shooting",
        ge=-120.0, le=45.0
    )
    gimbal_yaw: float = Field(
        default=0.0,
        serialization_alias="gimbalYawRotateAngle",
        description="Gimbal yaw angle for shooting",
        ge=-180.0, le=180.0
    )
    focus_x: int = Field(
        default=960//2 - 20,
        serialization_alias="focusX",
        description="Focus area upper left X coordinate in px",
        ge=0, le=960
    )
    focus_y: int = Field(
        default=720//2 - 20,
        serialization_alias="focusY",
        description="Focus area upper left Y coordinate in px",
        ge=0, le=720
    )
    focus_width: int = Field(
        default=40,
        serialization_alias="focusRegionWidth",
        serialization_description="Focus region width in px",
        ge=0, le=960
    )
    focus_height: int = Field(
        default=40,
        serialization_alias="focusRegionHeight",
        serialization_description="Focus region height in px",
        ge=0, le=720
    )
    focal_length: float = Field(
        default=24.0,
        serialization_alias="focalLength",
        description="Target focal length in mm",
        ge=0.0
    )
    drone_heading: float = Field(
        default=0.0,
        serialization_alias="aircraftHeading",
        description="Drone heading in degrees, 0 for North",
        ge=-180.0, le=180.0
    )
    ai_spot_check: int = Field(
        default=0,
        serialization_alias="accurateFrameValid",
        description="totally no idea what this is from the dji docs:\
                    1: Selected  0: Not selected  Note: This value sets to 1. Then the drone will automatically find \" \
                    the target and capture photos. This value sets to 0. Then the drone will repeat action according to \
                    the drone attitude and payload attitude. It will not automatically find the target.",
        ge=0, le=1
    )
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    payload_lens: PAYLOAD_LENS|str|None = Field(
        default=None,
        serialization_alias="payloadLensIndex",
        description="Payload lens index (None for default, or specific lens index)"
    )
    use_global_payload_lens_index: int = Field(
        default=0,
        serialization_alias="useGlobalPayloadLensIndex",
        description="Use global payload lens index (0: No, 1: Yes)" ,
        ge=0, le=1
    )
    target_angle: float = Field(
        default=0.0,
        serialization_alias="targetAngle",
        description="totally no idea what this is from the dji docs:\
                    Angle of target box. Note: The rotation angle. (Based on the y-axis and rotate clockwise.",
        ge=0, le=360.0
    )
    uuid: str|None = Field(
        default=None,
        serialization_alias="actionUUID",
        description="from dji offical doc: Note: This value will be written to the image file during the capturing to associate the action and image file."
    )
    
    @field_validator('payload_lens')
    @classmethod  
    def validate_payload_lens_oriented(cls, v):
        return validate_payload_lens(v)
    image_width: int = Field(
        default=960,
        serialization_alias="imageWidth",
        description="wtf why put fixed value here?",
        ge=960, le=960
    )
    image_height: int = Field(
        default=720,
        serialization_alias="imageHeight",
        description="wtf why put fixed value here?",
        ge=720, le=720
    )
    afpos: int|None = Field(
        default=None,
        serialization_alias="AFPos",
        description="dji even doesnt provide any description for this field. not sure default value is correct.",
    )
    gimbal_port: int = Field(
        default=0,
        serialization_alias="gimbalPort",
        description="from dji docs:\
                    Capturing camera installation position\
                    Note: This value of M30/M30T models are 0.",
        ge=0, le=0
    )
    camera_type: int = Field(
        default=52,
        serialization_alias="orientedCameraType",
        description="from dji docs: \
                    52 (Model: M30 dual light camera),\
                    53 (Model: M30T tripple light camera)",
        ge=0, le=100
    )
    file_path: str|None = Field(
        default=None,
        serialization_alias="orientedFilePath",
        description="no description from dji offical doc, doc says required field not sure if this is correct"
    )
    file_md5: str|None = Field(
        default=None,
        serialization_alias="orientedFileMD5",
        description="why the hell this is required field? dji offical doc says this is required field, but no description provided",
    )
    file_size: int|None = Field(
        default=None,
        serialization_alias="orientedFileSize",
        description="Speechless. dji offical doc says this is required field, real image file size in bytes",
    )
    file_suffix: str = Field(
        default='',
        serialization_alias="orientedFileSuffix",
        description="File suffix is added when the generated media files are named.",
    )
    apertue: int|None = Field(
        default=None,
        serialization_alias="orientedCameraApertue",
        description="Note: This value is the real aperture x 100"
    )
    luminance: int|None = Field(
        default=None,
        serialization_alias="orientedCameraLuminance",
        description="from dji offical doc: Environment luminance"
    )
    exposure_time: float|None = Field(
        default=None,
        serialization_alias="orientedCameraShutterTime",
        description="from dji offical doc: 	Shutter time in second. it probably means exposure time",
    )
    iso: int|None = Field(
        default=None,
        serialization_alias="orientedCameraISO",
        description="ISO"
    )
    photo_mode: str = Field(
        default="normalPhoto",
        serialization_alias="orientedPhotoMode",
        description="from dji offical doc:\
                    normalPhoto: Normal photo\
                    lowLightSmartShooting: Smart Low-Light"
    )
    @field_validator("photo_mode")
    @classmethod
    def validate_photo_mode(cls, v: str) -> str:
        """Validate photo mode."""
        valid_modes = ["normalPhoto", "lowLightSmartShooting"]
        if v not in valid_modes:
            raise ValueError(f"Invalid photo mode: {v}. Must be one of {valid_modes}.")
        return v

@register_action(ActionType.PANO_SHOT)
class PanoShotAction(Action):
    """Pano shot action for capturing panoramic images."""
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    payload_lens: PAYLOAD_LENS|str|None = Field(
        default=None,
        serialization_alias="payloadLensIndex",
        description="Payload lens index (None for default, or specific lens index)"
    )
    use_global_payload_lens_index: int = Field(
        default=0,
        serialization_alias="useGlobalPayloadLensIndex",
        description="Use global payload lens index (0: No, 1: Yes)" ,
        ge=0, le=1
    )
    pano_mode: str = Field(
        default="panoShot_360",
        serialization_alias="panoShotSubMode",
        description="dji offical doc:\
                    panoShot_360: Panorama mode"
    )
    
    @field_validator('payload_lens')
    @classmethod  
    def validate_payload_lens_pano(cls, v):
        return validate_payload_lens(v)

class POINT_CLOUD_OPERATION(str, Enum):
    """Enum for point cloud recording operations."""
    START_RECORD = "startRecord"
    STOP_RECORD = "stopRecord"
    PAUSE_RECORD = "pauseRecord"
    RESUME_RECORD = "resumeRecord"

    def __str__(self):
        return self.value

@register_action(ActionType.RECORD_POINT_CLOUD)
class RecordPointCloudAction(Action):
    """Record point cloud action for capturing 3D point cloud data."""
    payload_position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Payload position index",
        ge=0, le=2
    )
    operation: POINT_CLOUD_OPERATION = Field(
        default=POINT_CLOUD_OPERATION.START_RECORD,
        serialization_alias="recordPointCloudOperate",
        description="Operation type (start, stop, pause, resume)",
    )