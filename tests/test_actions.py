"""
Comprehensive test suite for DJI KMZ action classes.

This test file covers all the action classes with detailed tests for the
most important actions (TakePhoto, Hover, GimbalRotate, RotateYaw) and
basic tests for the other actions.
"""

import pytest
from pydantic import ValidationError
import xmltodict
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from djikmz.model.action import (
    Action,
    ActionType,
    TakePhotoAction,
    StartRecordAction,
    StopRecordAction,
    GimbalRotateAction,
    GimbalEvenlyRotateAction,
    HoverAction,
    RotateYawAction,
    FocusAction,
    ZoomAction,
    AccurateShootAction,
    OrientedShootAction,
    ACTION_REGISTRY
)
from djikmz.model.action.camera_actions import PAYLOAD_LENS


class TestActionType:
    """Test ActionType enum."""
    
    def test_action_type_values(self):
        """Test that ActionType has correct values."""
        assert ActionType.TAKE_PHOTO == "takePhoto"
        assert ActionType.HOVER == "hover"
        assert ActionType.ROTATE_YAW == "rotateYaw"
        assert ActionType.GIMBAL_ROTATE == "gimbalRotate"
        
    def test_action_type_str(self):
        """Test ActionType string representation."""
        assert str(ActionType.TAKE_PHOTO) == "takePhoto"
        assert str(ActionType.HOVER) == "hover"
    
    def test_action_type_immutable(self):
        """Test that action_type field is immutable after initialization."""
        action = TakePhotoAction()
        with pytest.raises((ValidationError, AttributeError)):
            action.action_type = ActionType.HOVER


class TestActionRegistry:
    """Test action registry functionality."""
    
    def test_all_actions_registered(self):
        """Test that all action types are registered."""
        expected_types = {
            ActionType.TAKE_PHOTO,
            ActionType.START_RECORD,
            ActionType.STOP_RECORD,
            ActionType.GIMBAL_ROTATE,
            ActionType.GIMBAL_EVENLY_ROTATE,
            ActionType.HOVER,
            ActionType.ROTATE_YAW,
            ActionType.FOCUS,
            ActionType.ZOOM,
            ActionType.ACCURATE_SHOOT,
            ActionType.ORIENTED_SHOOT,
        }
        registered_types = set(ACTION_REGISTRY.keys())
        assert expected_types.issubset(registered_types)
    
    def test_action_classes_correct(self):
        """Test that correct action classes are registered."""
        assert ACTION_REGISTRY[ActionType.TAKE_PHOTO] == TakePhotoAction
        assert ACTION_REGISTRY[ActionType.HOVER] == HoverAction
        assert ACTION_REGISTRY[ActionType.ROTATE_YAW] == RotateYawAction
        assert ACTION_REGISTRY[ActionType.GIMBAL_ROTATE] == GimbalRotateAction


class TestTakePhotoAction:
    """Comprehensive tests for TakePhotoAction."""
    
    def test_creation_with_defaults(self):
        """Test creating TakePhotoAction with default values."""
        action = TakePhotoAction()
        assert action.action_id == 0
        assert action.action_type == ActionType.TAKE_PHOTO
        assert action.payload_position == 0
        assert action.file_suffix == ''
        assert action.payload_lens is None
    
    def test_creation_with_custom_values(self):
        """Test creating TakePhotoAction with custom values."""
        action = TakePhotoAction(
            action_id=42,
            payload_position=1,
            file_suffix="test_photo",
            payload_lens=PAYLOAD_LENS.ZOOM
        )
        assert action.action_id == 42
        assert action.payload_position == 1
        assert action.file_suffix == "test_photo"
        assert action.payload_lens == PAYLOAD_LENS.ZOOM
    
    def test_payload_position_validation(self):
        """Test payload position validation."""
        # Valid values
        TakePhotoAction(payload_position=0)
        TakePhotoAction(payload_position=1)
        TakePhotoAction(payload_position=2)
        
        # Invalid values
        with pytest.raises(ValidationError):
            TakePhotoAction(payload_position=-1)
        with pytest.raises(ValidationError):
            TakePhotoAction(payload_position=3)
    
    def test_payload_lens_validation(self):
        """Test payload lens validation."""
        # Valid enum value
        action = TakePhotoAction(payload_lens=PAYLOAD_LENS.WIDE)
        assert action.payload_lens == PAYLOAD_LENS.WIDE
        
        # Valid string value
        action = TakePhotoAction(payload_lens="zoom")
        assert action.payload_lens == PAYLOAD_LENS.ZOOM
        
        # None value
        action = TakePhotoAction(payload_lens=None)
        assert action.payload_lens is None
    
    def test_action_id_validation(self):
        """Test action ID validation."""
        # Valid values
        TakePhotoAction(action_id=0)
        TakePhotoAction(action_id=65535)
        
        # Invalid values
        with pytest.raises(ValidationError):
            TakePhotoAction(action_id=-1)
        with pytest.raises(ValidationError):
            TakePhotoAction(action_id=65536)
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        action = TakePhotoAction(
            action_id=1,
            payload_position=1,
            file_suffix="test",
            payload_lens=PAYLOAD_LENS.ZOOM
        )
        result = action.to_dict()
        
        # Check header fields
        assert result["wpml:actionId"] == 1
        assert result["wpml:actionActuatorFunc"] == "takePhoto"
        
        # Check action parameters
        params = result["wpml:actionActuatorFuncParam"]
        assert params["wpml:payloadPositionIndex"] == 1
        assert params["wpml:fileSuffix"] == "test"
        assert params["wpml:payloadLensIndex"] == "zoom"
    
    def test_xml_serialization(self):
        """Test XML serialization and deserialization."""
        action = TakePhotoAction(
            action_id=1,
            payload_position=1,
            file_suffix="test"
        )
        
        # Serialize to XML
        xml_str = action.to_xml()
        assert "wpml:actionId" in xml_str
        assert "takePhoto" in xml_str
        assert "test" in xml_str
        
        # Deserialize from XML
        xml_with_root = f'<wpml:action>{xml_str}</wpml:action>'
        recreated_action = TakePhotoAction.from_xml(xml_with_root)
        assert recreated_action.action_id == action.action_id
        assert recreated_action.action_type == action.action_type
        assert recreated_action.file_suffix == action.file_suffix


class TestHoverAction:
    """Comprehensive tests for HoverAction."""
    
    def test_creation_with_defaults(self):
        """Test creating HoverAction with default values."""
        action = HoverAction()
        assert action.action_id == 0
        assert action.action_type == ActionType.HOVER
        assert action.hover_time == 1.0
    
    def test_creation_with_custom_values(self):
        """Test creating HoverAction with custom values."""
        action = HoverAction(action_id=5, hover_time=10.5)
        assert action.action_id == 5
        assert action.hover_time == 10.5
    
    def test_hover_time_validation(self):
        """Test hover time validation."""
        # Valid values
        HoverAction(hover_time=0.1)
        HoverAction(hover_time=1.0)
        HoverAction(hover_time=999.9)
        
        # Invalid values
        with pytest.raises(ValidationError):
            HoverAction(hover_time=0.0)
        with pytest.raises(ValidationError):
            HoverAction(hover_time=-1.0)
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        action = HoverAction(action_id=2, hover_time=5.0)
        result = action.to_dict()
        
        assert result["wpml:actionId"] == 2
        assert result["wpml:actionActuatorFunc"] == "hover"
        params = result["wpml:actionActuatorFuncParam"]
        assert params["wpml:hoverTime"] == 5.0
    
    def test_xml_roundtrip(self):
        """Test XML serialization roundtrip."""
        action = HoverAction(action_id=3, hover_time=7.5)
        xml_str = action.to_xml()
        xml_with_root = f'<wpml:action>{xml_str}</wpml:action>'
        recreated_action = HoverAction.from_xml(xml_with_root)
        
        assert recreated_action.action_id == action.action_id
        assert recreated_action.hover_time == action.hover_time


class TestGimbalRotateAction:
    """Comprehensive tests for GimbalRotateAction."""
    
    def test_creation_with_defaults(self):
        """Test creating GimbalRotateAction with default values."""
        action = GimbalRotateAction()
        assert action.action_id == 0
        assert action.action_type == ActionType.GIMBAL_ROTATE
        assert action.payload_position == 0
        assert action.gimbal_rotate_mode == "absoluteAngle"
        assert action.gimbal_pitch_rotate_enable == 0
        assert action.gimbal_pitch_rotate_angle == 0.0
        assert action.gimbal_roll_rotate_enable == 0
        assert action.gimbal_roll_rotate_angle == 0.0
        assert action.gimbal_yaw_rotate_enable == 0
        assert action.gimbal_yaw_rotate_angle == 0.0
    
    def test_creation_with_custom_values(self):
        """Test creating GimbalRotateAction with custom values."""
        action = GimbalRotateAction(
            action_id=10,
            payload_position=1,
            gimbal_pitch_rotate_enable=1,
            gimbal_pitch_rotate_angle=-45.0,
            gimbal_yaw_rotate_enable=1,
            gimbal_yaw_rotate_angle=90.0
        )
        assert action.action_id == 10
        assert action.payload_position == 1
        assert action.gimbal_pitch_rotate_enable == 1
        assert action.gimbal_pitch_rotate_angle == -45.0
        assert action.gimbal_yaw_rotate_enable == 1
        assert action.gimbal_yaw_rotate_angle == 90.0
    
    def test_payload_position_validation(self):
        """Test payload position validation."""
        # Valid values
        GimbalRotateAction(payload_position=0)
        GimbalRotateAction(payload_position=2)
        
        # Invalid values
        with pytest.raises(ValidationError):
            GimbalRotateAction(payload_position=-1)
        with pytest.raises(ValidationError):
            GimbalRotateAction(payload_position=3)
    
    def test_gimbal_rotate_mode_validation(self):
        """Test gimbal rotate mode validation."""
        # Valid value
        GimbalRotateAction(gimbal_rotate_mode="absoluteAngle")
        
        # Invalid value
        with pytest.raises(ValidationError):
            GimbalRotateAction(gimbal_rotate_mode="invalidMode")
    
    def test_enable_flags_validation(self):
        """Test enable flags validation."""
        # Valid values (0 and 1)
        GimbalRotateAction(gimbal_pitch_rotate_enable=0)
        GimbalRotateAction(gimbal_pitch_rotate_enable=1)
        GimbalRotateAction(gimbal_roll_rotate_enable=0)
        GimbalRotateAction(gimbal_yaw_rotate_enable=1)
        
        # Invalid values
        with pytest.raises(ValidationError):
            GimbalRotateAction(gimbal_pitch_rotate_enable=-1)
        with pytest.raises(ValidationError):
            GimbalRotateAction(gimbal_roll_rotate_enable=2)
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        action = GimbalRotateAction(
            action_id=4,
            gimbal_pitch_rotate_enable=1,
            gimbal_pitch_rotate_angle=-30.0
        )
        result = action.to_dict()
        
        assert result["wpml:actionId"] == 4
        assert result["wpml:actionActuatorFunc"] == "gimbalRotate"
        params = result["wpml:actionActuatorFuncParam"]
        assert params["wpml:gimbalPitchRotateEnable"] == 1
        assert params["wpml:gimbalPitchRotateAngle"] == -30.0


class TestRotateYawAction:
    """Comprehensive tests for RotateYawAction."""
    
    def test_creation_with_defaults(self):
        """Test creating RotateYawAction with default values."""
        action = RotateYawAction()
        assert action.action_id == 0
        assert action.action_type == ActionType.ROTATE_YAW
        assert action.aircraft_heading == 0.0
        assert action.direction == "clockwise"
    
    def test_creation_with_custom_values(self):
        """Test creating RotateYawAction with custom values."""
        action = RotateYawAction(
            action_id=15,
            aircraft_heading=90.0,
            direction="counterClockwise"
        )
        assert action.action_id == 15
        assert action.aircraft_heading == 90.0
        assert action.direction == "counterClockwise"
    
    def test_aircraft_heading_validation(self):
        """Test aircraft heading validation."""
        # Valid values
        RotateYawAction(aircraft_heading=-180.0)
        RotateYawAction(aircraft_heading=0.0)
        RotateYawAction(aircraft_heading=180.0)
        
        # Invalid values
        with pytest.raises(ValidationError):
            RotateYawAction(aircraft_heading=-180.1)
        with pytest.raises(ValidationError):
            RotateYawAction(aircraft_heading=180.1)
    
    def test_direction_validation(self):
        """Test direction validation."""
        # Valid values
        RotateYawAction(direction="clockwise")
        RotateYawAction(direction="counterClockwise")
        
        # Invalid value
        with pytest.raises(ValidationError):
            RotateYawAction(direction="invalid_direction")
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        action = RotateYawAction(
            action_id=20,
            aircraft_heading=45.0,
            direction="counterClockwise"
        )
        result = action.to_dict()
        
        assert result["wpml:actionId"] == 20
        assert result["wpml:actionActuatorFunc"] == "rotateYaw"
        params = result["wpml:actionActuatorFuncParam"]
        assert params["wpml:aircraftHeading"] == 45.0
        assert params["wpml:aircraftPathMode"] == "counterClockwise"


class TestRecordActions:
    """Basic tests for recording actions."""
    
    def test_start_record_action(self):
        """Test StartRecordAction creation and basic functionality."""
        action = StartRecordAction(action_id=1)
        assert action.action_type == ActionType.START_RECORD
        assert action.action_id == 1
        
        result = action.to_dict()
        assert result["wpml:actionActuatorFunc"] == "startRecord"
    
    def test_stop_record_action(self):
        """Test StopRecordAction creation and basic functionality."""
        action = StopRecordAction(action_id=2)
        assert action.action_type == ActionType.STOP_RECORD
        assert action.action_id == 2
        
        result = action.to_dict()
        assert result["wpml:actionActuatorFunc"] == "stopRecord"


class TestFocusAction:
    """Basic tests for FocusAction."""
    
    def test_creation_with_defaults(self):
        """Test creating FocusAction with default values."""
        action = FocusAction()
        assert action.action_type == ActionType.FOCUS
        assert action.payload_position == 0
        assert action.is_point_focus == 0
    
    def test_creation_with_custom_values(self):
        """Test creating FocusAction with custom values."""
        action = FocusAction(
            action_id=5,
            payload_position=1,
            is_point_focus=1,
            focus_x=0.5,
            focus_y=0.3
        )
        assert action.action_id == 5
        assert action.payload_position == 1
        assert action.is_point_focus == 1
        assert action.focus_x == 0.5
        assert action.focus_y == 0.3
    
    def test_focus_coordinates_validation(self):
        """Test focus coordinates validation."""
        # Valid values
        FocusAction(focus_x=0.0, focus_y=0.0)
        FocusAction(focus_x=1.0, focus_y=1.0)
        
        # Invalid values
        with pytest.raises(ValidationError):
            FocusAction(focus_x=-0.1)
        with pytest.raises(ValidationError):
            FocusAction(focus_y=1.1)


class TestZoomAction:
    """Basic tests for ZoomAction."""
    
    def test_creation_with_defaults(self):
        """Test creating ZoomAction with default values."""
        action = ZoomAction()
        assert action.action_type == ActionType.ZOOM
        assert action.payload_position == 0
        assert action.focal_length == 24.0
    
    def test_creation_with_custom_values(self):
        """Test creating ZoomAction with custom values."""
        action = ZoomAction(
            action_id=10,
            payload_position=2,
            focal_length=85.0
        )
        assert action.action_id == 10
        assert action.payload_position == 2
        assert action.focal_length == 85.0
    
    def test_focal_length_validation(self):
        """Test focal length validation."""
        # Valid values
        ZoomAction(focal_length=24.0)
        ZoomAction(focal_length=200.0)
        
        # Invalid values
        with pytest.raises(ValidationError):
            ZoomAction(focal_length=0.0)
        with pytest.raises(ValidationError):
            ZoomAction(focal_length=-10.0)


class TestShootingActions:
    """Basic tests for shooting actions."""
    
    def test_accurate_shoot_action(self):
        """Test AccurateShootAction creation and basic functionality."""
        action = AccurateShootAction(action_id=1)
        assert action.action_type == ActionType.ACCURATE_SHOOT
        assert action.payload_position == 0
        
        result = action.to_dict()
        assert result["wpml:actionActuatorFunc"] == "accurateShoot"
    
    def test_oriented_shoot_action(self):
        """Test OrientedShootAction creation and basic functionality."""
        action = OrientedShootAction(
            action_id=2,
            payload_position=1,
            gimbal_pitch=-45.0,
            drone_heading=90.0
        )
        assert action.action_type == ActionType.ORIENTED_SHOOT
        assert action.payload_position == 1
        assert action.gimbal_pitch == -45.0
        assert action.drone_heading == 90.0


class TestGimbalEvenlyRotateAction:
    """Basic tests for GimbalEvenlyRotateAction."""
    
    def test_creation_with_defaults(self):
        """Test creating GimbalEvenlyRotateAction with default values."""
        action = GimbalEvenlyRotateAction()
        assert action.action_type == ActionType.GIMBAL_EVENLY_ROTATE
        assert action.payload_position == 0
        assert action.pitch_rotate_angle == 0.0
    
    def test_creation_with_custom_values(self):
        """Test creating GimbalEvenlyRotateAction with custom values."""
        action = GimbalEvenlyRotateAction(
            action_id=8,
            pitch_rotate_angle=-60.0
        )
        assert action.action_id == 8
        assert action.pitch_rotate_angle == -60.0


class TestXMLSerialization:
    """Test XML serialization/deserialization for various actions."""
    
    def test_xml_roundtrip_multiple_actions(self):
        """Test XML roundtrip for multiple action types."""
        actions = [
            TakePhotoAction(action_id=1, file_suffix="test1"),
            HoverAction(action_id=2, hover_time=5.0),
            RotateYawAction(action_id=3, aircraft_heading=90.0),
            GimbalRotateAction(action_id=4, gimbal_pitch_rotate_enable=1)
        ]
        
        for action in actions:
            xml_str = action.to_xml()
            xml_with_root = f'<wpml:action>{xml_str}</wpml:action>'
            
            # Parse back to verify structure
            parsed = xmltodict.parse(xml_with_root)
            assert "wpml:action" in parsed
            assert "wpml:actionId" in parsed["wpml:action"]
            assert "wpml:actionActuatorFunc" in parsed["wpml:action"]
            
            # Recreate and verify basic properties
            recreated = action.__class__.from_xml(xml_with_root)
            assert recreated.action_id == action.action_id
            assert recreated.action_type == action.action_type


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
