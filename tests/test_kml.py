"""
Test cases for KML module.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

# Fix the import in kml.py first
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from djikmz.model.kml import KML, WaypointTurnMode, GimbalPitchMode
from djikmz.model.mission_config import MissionConfig
from djikmz.model.coordinate_system_param import CoordinateSystemParam
from djikmz.model.heading_param import WaypointHeadingParam
from djikmz.model.turn_param import WaypointTurnParam
from djikmz.model.waypoint import Waypoint


class TestKML:
    """Test KML class."""
    
    def test_kml_creation_with_defaults(self):
        """Test creating KML with default values."""
        kml = KML()
        
        assert kml.author == "Zey"
        assert kml.template_type == "waypoint"
        assert kml.template_id == 0
        assert kml.global_speed == 1.0
        assert kml.global_height == 0.0
        assert kml.global_turn_mode == WaypointTurnMode.TURN_AT_POINT
        assert kml.global_use_straight_line == 1
        assert kml.global_gimbal_pitch_mode == GimbalPitchMode.MANUAL
        assert len(kml.waypoints) == 0
        assert isinstance(kml.mission_config, MissionConfig)
        assert isinstance(kml.coordinate_system_param, CoordinateSystemParam)
        assert isinstance(kml.global_waypoint_heading_param, WaypointHeadingParam)
    
    def test_kml_creation_with_custom_values(self):
        """Test creating KML with custom values."""
        custom_time = int(datetime(2023, 1, 1).timestamp() * 1000)
        
        kml = KML(
            author="TestUser",
            create_time=custom_time,
            update_time=custom_time,
            global_speed=5.0,
            global_height=100.0,
            global_turn_mode=WaypointTurnMode.COORDINATED_TURN,
            global_use_straight_line=0,
            global_gimbal_pitch_mode=GimbalPitchMode.POINT_SETTING
        )
        
        assert kml.author == "TestUser"
        assert kml.create_time == custom_time
        assert kml.update_time == custom_time
        assert kml.global_speed == 5.0
        assert kml.global_height == 100.0
        assert kml.global_turn_mode == WaypointTurnMode.COORDINATED_TURN
        assert kml.global_use_straight_line == 0
        assert kml.global_gimbal_pitch_mode == GimbalPitchMode.POINT_SETTING
    
    def test_kml_with_waypoints(self):
        """Test creating KML with waypoints."""
        # Create test waypoints
        waypoint1 = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            height=100.0
        )
        waypoint2 = Waypoint(
            latitude=37.7849,
            longitude=-122.4094,
            height=120.0
        )
        
        kml = KML(waypoints=[waypoint1, waypoint2])
        
        assert len(kml.waypoints) == 2
        assert kml.waypoints[0].latitude == 37.7749
        assert kml.waypoints[1].latitude == 37.7849
    
    def test_to_xml_basic(self):
        """Test basic XML output."""
        kml = KML(
            author="TestUser",
            global_speed=2.0,
            global_height=50.0
        )
        
        xml_output = kml.to_xml()
        
        # Check that it's valid XML-like string
        assert isinstance(xml_output, str)
        assert len(xml_output) > 0
        
        # Check for key elements
        assert "wpml:author" in xml_output
        assert "TestUser" in xml_output
        assert "wpml:autoFlightSpeed" in xml_output
        assert "2.0" in xml_output
        assert "wpml:globalHeight" in xml_output
        assert "50.0" in xml_output
        assert "wpml:templateType" in xml_output
        assert "waypoint" in xml_output
        assert "Folder" in xml_output
    
    def test_to_xml_with_waypoints(self):
        """Test XML output with waypoints."""
        waypoint = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            height=100.0
        )
        
        kml = KML(
            author="TestUser",
            waypoints=[waypoint]
        )
        
        xml_output = kml.to_xml()
        
        # Check for waypoint elements
        assert "Placemark" in xml_output
        assert "37.7749" in xml_output
        assert "-122.4194" in xml_output
        assert "100.0" in xml_output
    
    def test_to_xml_structure(self):
        """Test XML structure contains expected wpml prefixes."""
        kml = KML()
        xml_output = kml.to_xml()
        
        # Check for wpml prefixed elements
        wpml_elements = [
            "wpml:author",
            "wpml:createTime", 
            "wpml:updateTime",
            "wpml:missionConfig",
            "wpml:templateType",
            "wpml:templateId",
            "wpml:waylineCoordinateSysParam",
            "wpml:autoFlightSpeed",
            "wpml:globalHeight",
            "wpml:globalWaypointHeadingParam",
            "wpml:globalWaypointTurnMode",
            "wpml:globalUseStraightLine",
            "wpml:globalGimbalPitchMode"
        ]
        
        for element in wpml_elements:
            assert element in xml_output, f"Missing element: {element}"
    
    def test_to_xml_folder_structure(self):
        """Test that XML has proper folder structure."""
        kml = KML()
        xml_output = kml.to_xml()
        
        # Check that Folder element exists
        assert "Folder" in xml_output
        
        # Check that root level and folder level elements are properly separated
        # Root level elements should not be in folder
        # assert xml_output.find("wpml:templateType") > xml_output.find("Folder")
        assert xml_output.find("wpml:author") < xml_output.find("Folder")
        assert xml_output.find("wpml:createTime") < xml_output.find("Folder")
        assert xml_output.find("wpml:updateTime") < xml_output.find("Folder")
        # Folder elements should be in folder
        folder_start = xml_output.find("Folder")
        # assert xml_output.find("wpml:author", folder_start) > folder_start
        # assert xml_output.find("wpml:missionConfig", folder_start) > folder_start
        assert xml_output.find("wpml:waylineCoordinateSysParam", folder_start) > folder_start
        assert xml_output.find("wpml:autoFlightSpeed", folder_start) > folder_start
        assert xml_output.find("wpml:globalHeight", folder_start) > folder_start
        assert xml_output.find("wpml:globalWaypointHeadingParam", folder_start) > folder_start
        assert xml_output.find("wpml:globalWaypointTurnMode", folder_start) > folder_start
        assert xml_output.find("wpml:globalUseStraightLine", folder_start) > folder_start
        assert xml_output.find("wpml:globalGimbalPitchMode", folder_start) > folder_start
    
    def test_to_xml_roundtrip_basic(self):
        """Test basic XML serialization roundtrip."""
        original = KML(
            author="RoundtripTest",
            global_speed=3.0,
            global_height=75.0,
            global_turn_mode=WaypointTurnMode.CURVED_TURN_WITH_STOP
        )
        
        # Convert to XML and back
        xml_output = original.to_xml()
        xml_output = xml_output 
        recreated = KML.from_xml(xml_output)
        
        assert recreated.author == original.author
        assert recreated.global_speed == original.global_speed
        assert recreated.global_height == original.global_height
        assert recreated.global_turn_mode == original.global_turn_mode
        assert recreated.template_type == original.template_type
        assert recreated.template_id == original.template_id
    
    def test_to_xml_pretty_formatted(self):
        """Test that XML output is pretty formatted."""
        kml = KML()
        xml_output = kml.to_xml()
        
        # Check for indentation (should have newlines and spaces for pretty formatting)
        assert "\n" in xml_output
        assert "  " in xml_output or "\t" in xml_output  # Some form of indentation
    
    def test_to_xml_with_complex_waypoint(self):
        """Test XML output with a complex waypoint."""
        from djikmz.model.action.camera_actions import TakePhotoAction
        from djikmz.model.action_group import ActionGroup
        
        # Create an action
        action = TakePhotoAction(action_id=1, payload_position=0, file_suffix="test")
        action_group = ActionGroup(
            action_group_id=1,
            action_group_start_index=0,
            action_group_end_index=0,
            action_group_mode=0,
            actions=[action]
        )
        
        # Create waypoint with action
        waypoint = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            height=100.0,
            action_group=action_group
        )
        
        kml = KML(waypoints=[waypoint])
        xml_output = kml.to_xml()
        
        # Check that action data is included
        assert "wpml:actionGroup" in xml_output
        assert "wpml:actionGroupId" in xml_output
        assert "takePhoto" in xml_output


class TestKMLValidation:
    """Test KML validation."""
    
    def test_template_type_validation(self):
        """Test template type validation."""
        # Valid template type
        kml = KML(template_type="waypoint")
        assert kml.template_type == "waypoint"
        
        # Invalid template type should raise validation error
        with pytest.raises(ValidationError):
            KML(template_type="invalid")
    
    def test_template_id_validation(self):
        """Test template ID validation."""
        # Valid template ID
        kml = KML(template_id=0)
        assert kml.template_id == 0
        
        # Invalid template IDs
        with pytest.raises(ValidationError):
            KML(template_id=1)
        
        with pytest.raises(ValidationError):
            KML(template_id=-1)
    
    def test_global_speed_validation(self):
        """Test global speed validation."""
        # Valid speeds
        KML(global_speed=0.0)
        KML(global_speed=10.0)
        
        # Invalid speed
        with pytest.raises(ValidationError):
            KML(global_speed=-1.0)
    
    def test_global_height_validation(self):
        """Test global height validation."""
        # Valid heights
        KML(global_height=0.0)
        KML(global_height=1000.0)
        
        # Invalid height
        with pytest.raises(ValidationError):
            KML(global_height=-1.0)
    
    def test_global_use_straight_line_validation(self):
        """Test global use straight line validation."""
        # Valid values
        KML(global_use_straight_line=0)
        KML(global_use_straight_line=1)
        
        # Invalid values
        with pytest.raises(ValidationError):
            KML(global_use_straight_line=2)
        
        with pytest.raises(ValidationError):
            KML(global_use_straight_line=-1)


class TestKMLEnums:
    """Test KML enum classes."""
    
    def test_waypoint_turn_mode_enum(self):
        """Test WaypointTurnMode."""
        assert WaypointTurnMode.COORDINATED_TURN == "coordinateTurn"
        assert WaypointTurnMode.TURN_AT_POINT == "toPointAndStopWithDiscontinuityCurvature"
        assert WaypointTurnMode.CURVED_TURN_WITHOUT_STOP == "toPointAndPassWithContinuityCurvature"
        assert WaypointTurnMode.CURVED_TURN_WITH_STOP == "toPointAndStopWithContinuityCurvature"
        
        # Test string representation
        assert str(WaypointTurnMode.COORDINATED_TURN) == "coordinateTurn"
    
    def test_gimbal_pitch_mode_enum(self):
        """Test GimbalPitchMode."""
        assert GimbalPitchMode.MANUAL == "manual"
        assert GimbalPitchMode.POINT_SETTING == "usePointSetting"
        
        # Test string representation
        assert str(GimbalPitchMode.MANUAL) == "manual"


if __name__ == "__main__":
    # Simple test runner for debugging
    test_kml = TestKML()
    
    print("Testing KML.to_xml() basic functionality...")
    test_kml.test_to_xml_basic()
    print("✓ Basic XML test passed")
    
    test_kml.test_to_xml_structure()
    print("✓ XML structure test passed")
    
    test_kml.test_to_xml_folder_structure()
    print("✓ XML folder structure test passed")
    
    print("\nAll tests passed!")
