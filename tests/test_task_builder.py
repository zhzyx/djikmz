"""
Test cases for TaskBuilder functionality.

These tests cover the TaskBuilder API, validation, and KMZ generation.
Includes a test that generates a real KMZ file for DJI controller testing.
"""

import pytest
import sys
import tempfile
import os
import zipfile
from pathlib import Path

# Add src to path for local imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from djikmz import DroneTask, ValidationError, HardwareError
from pydantic import ValidationError as PydanticValidationError
from djikmz.model import KML, Waypoint, PayloadModel
from djikmz.model.turn_param import WaypointTurnParam, WaypointTurnMode
from djikmz.task_builder import WaypointBuilder


class TestTaskBuilderBasic:
    """Test basic TaskBuilder functionality."""
    
    def test_drone_task_creation(self):
        """Test basic DroneTask creation."""
        task = DroneTask("M30T", "Test Pilot")
        assert task is not None
        
    def test_supported_drone_models(self):
        """Test that all supported drone models work."""
        supported_models = ["M350", "M300", "M30", "M30T", "M3E", "M3T", "M3M", "M3D", "M3TD"]
        
        for model in supported_models:
            task = DroneTask(model, "Test Pilot")
            assert task is not None
            
    def test_unsupported_drone_model(self):
        """Test that unsupported drone models raise HardwareError."""
        with pytest.raises(ValueError) as exc_info:
            DroneTask("Mini 3 Pro", "Test Pilot")
        
        assert "Unsupported drone model" in str(exc_info.value)
        assert "Mini 3 Pro" in str(exc_info.value)
        
    def test_mission_configuration(self):
        """Test mission configuration methods."""
        task = (DroneTask("M30T", "Test Pilot")
               .name("Test Mission")
               .speed(8.0)
               .altitude(75.0))
        
        # Should not raise any errors
        assert task is not None
        
    def test_coordinate_system_configuration(self):
        """Test coordinate system configuration."""
        # GPS should work for all drones
        task = (DroneTask("M30T", "Test Pilot")
               .coordinate_system("GPS"))
        assert task is not None
        
        # RTK should work for RTK-capable drones
        task = (DroneTask("M350", "Test Pilot")
               .coordinate_system("RTK"))
        assert task is not None
        
        # RTK should fail for non-RTK drones
        with pytest.raises(ValidationError) as exc_info:
            DroneTask("M3E", "Test Pilot").coordinate_system("RTK").build()
        assert "RTK positioning not supported" in str(exc_info.value)


class TestTaskBuilderWaypoints:
    """Test waypoint creation and actions."""
    
    def test_single_waypoint(self):
        """Test creating a mission with a single waypoint."""
        task = (DroneTask("M30T", "Test Pilot")
               .fly_to(37.7749, -122.4194))
        
        kml = task.build()
        assert len(kml.waypoints) == 1
        assert kml.waypoints[0].latitude == 37.7749
        assert kml.waypoints[0].longitude == -122.4194
        
    def test_multiple_waypoints(self):
        """Test creating a mission with multiple waypoints."""
        task = (DroneTask("M30T", "Test Pilot")
               .fly_to(37.7749, -122.4194)
               .fly_to(37.7750, -122.4195)
               .fly_to(37.7751, -122.4196))
        
        kml = task.build()
        assert len(kml.waypoints) == 3
        
    def test_coordinate_validation(self):
        """Test coordinate validation."""
        # Valid coordinates should work
        task = DroneTask("M30T", "Test Pilot").fly_to(37.7749, -122.4194)
        kml = task.build()
        assert len(kml.waypoints) == 1
        
        # Invalid latitude should raise ValidationError
        with pytest.raises(PydanticValidationError):
            DroneTask("M30T", "Test Pilot").fly_to(91.0, -122.4194).build()
            
        # Invalid longitude should raise ValidationError  
        with pytest.raises(PydanticValidationError):
            DroneTask("M30T", "Test Pilot").fly_to(37.7749, 181.0).build()


class TestTaskBuilderActions:
    """Test waypoint actions."""
    
    def test_photo_action(self):
        """Test take_photo action."""
        task = (DroneTask("M30T", "Test Pilot")
               .fly_to(37.7749, -122.4194)
               .take_photo("test_photo"))
        
        kml = task.build()
        waypoint = kml.waypoints[0]
        assert waypoint.action_group is not None
        assert len(waypoint.action_group.actions) == 1
        
        action = waypoint.action_group.actions[0]
        assert action.action_type == "takePhoto"
        
    def test_hover_action(self):
        """Test hover action."""
        task = (DroneTask("M30T", "Test Pilot")
               .fly_to(37.7749, -122.4194)
               .hover(5.0))
        
        kml = task.build()
        waypoint = kml.waypoints[0]
        action = waypoint.action_group.actions[0]
        assert action.action_type == "hover"
        assert action.hover_time == 5.0
        
    def test_gimbal_actions(self):
        """Test various gimbal actions."""
        # Test gimbal_down
        task = (DroneTask("M30T", "Test Pilot")
               .fly_to(37.7749, -122.4194)
               .gimbal_down(45))
        
        kml = task.build()
        action = kml.waypoints[0].action_group.actions[0]
        assert action.action_type == "gimbalRotate"
        assert action.gimbal_pitch_rotate_enable == 1
        assert action.gimbal_pitch_rotate_angle == -45.0
        
        # Test gimbal_front
        task = (DroneTask("M30T", "Test Pilot")
               .fly_to(37.7749, -122.4194)
               .gimbal_front())
        
        kml = task.build()
        action = kml.waypoints[0].action_group.actions[0]
        assert action.gimbal_pitch_rotate_angle == 0.0
        
        # Test gimbal_rotate
        task = (DroneTask("M30T", "Test Pilot")
               .fly_to(37.7749, -122.4194)
               .gimbal_rotate(pitch=-30, yaw=90))
        
        kml = task.build()
        action = kml.waypoints[0].action_group.actions[0]
        assert action.gimbal_pitch_rotate_enable == 1
        assert action.gimbal_pitch_rotate_angle == -30.0
        assert action.gimbal_yaw_rotate_enable == 1
        assert action.gimbal_yaw_rotate_angle == 90.0
        
    def test_multiple_actions_per_waypoint(self):
        """Test multiple actions on a single waypoint."""
        task = (DroneTask("M30T", "Test Pilot")
               .fly_to(37.7749, -122.4194)
               .take_photo("test1")
               .hover(2.0)
               .gimbal_down(45)
               .take_photo("test2"))
        
        kml = task.build()
        waypoint = kml.waypoints[0]
        assert len(waypoint.action_group.actions) == 4


class TestTaskBuilderValidation:
    """Test TaskBuilder validation."""
    
    def test_empty_mission_validation(self):
        """Test that empty missions are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DroneTask("M30T", "Test Pilot").build()
        
        assert "Mission must have at least one waypoint" in str(exc_info.value)
        
    def test_speed_validation(self):
        """Test speed limit validation."""
        with pytest.raises(ValidationError) as exc_info:
            (DroneTask("M30T", "Test Pilot")
             .speed(50.0)  # Way too fast
             .fly_to(37.7749, -122.4194)
             .build())
        
        assert "Speed" in str(exc_info.value)
        assert "exceeds drone limit" in str(exc_info.value)
        
    def test_altitude_validation(self):
        """Test altitude validation."""
        # Test reasonable altitude
        task = (DroneTask("M30T", "Test Pilot")
               .altitude(100.0)
               .fly_to(37.7749, -122.4194))
        kml = task.build()
        assert kml is not None


class TestTaskBuilderKMZGeneration:
    """Test KMZ file generation and XML output."""
    
    def test_kml_generation(self):
        """Test basic KML generation."""
        task = (DroneTask("M30T", "Test Pilot")
               .name("Test Mission")
               .fly_to(37.7749, -122.4194)
               .take_photo("test"))
        
        kml = task.build()
        assert isinstance(kml, KML)
        assert kml.mission_config is not None
        assert len(kml.waypoints) == 1
        
    def test_xml_output(self):
        """Test XML output generation."""
        task = (DroneTask("M30T", "Test Pilot")
               .name("Test Mission")
               .fly_to(37.7749, -122.4194))
        
        kml = task.build()
        xml_output = kml.to_xml()
        
        assert isinstance(xml_output, str)
        assert "<?xml" in xml_output
        assert "kml" in xml_output
        assert "wpml:" in xml_output
        
    def test_real_world_dji_controller_mission(self):
        """
        Generate a real KMZ file for testing on DJI controller.
        
        This creates a comprehensive mission that can be loaded into 
        DJI Pilot 2 or DJI FlightHub 2 for real-world testing.
        """
        # Create a realistic survey mission
        mission = (DroneTask("M30T", "Survey Pilot")
                  .name("DJI Controller Test Mission")
                  .speed(8.0)      # Conservative speed
                  .altitude(60.0)   # Safe altitude
                  .coordinate_system("GPS")
                  .return_home_on_signal_loss(True)
                  
                  # Survey pattern - rectangular grid
                  .fly_to(37.7749, -122.4194)  # Start point
                      .take_photo("start_point")
                      .hover(2.0)
                      
                  .fly_to(37.7750, -122.4194)  # Move north
                      .gimbal_down(45)
                      .take_photo("north_point")
                      .hover(1.0)
                      
                  .fly_to(37.7750, -122.4195)  # Move east
                      .gimbal_front()
                      .take_photo("northeast_point")
                      .hover(1.0)
                      
                  .fly_to(37.7749, -122.4195)  # Move south
                      .gimbal_pitch(-90)  # Nadir view
                      .take_photo("southeast_nadir")
                      .hover(2.0)
                      
                  .fly_to(37.7749, -122.4194)  # Return to start
                      .gimbal_front()
                      .take_photo("end_point")
                      .hover(3.0))
        
        # Build and verify mission structure
        kml = mission.build()
        assert len(kml.waypoints) == 5
        assert kml.mission_config.drone_info.drone_enum_value == 67  # M30T
        
        # Create test directory
        test_dir = Path("test_output")
        test_dir.mkdir(exist_ok=True)
        
        # Generate KMZ file using the proper method
        kmz_file = test_dir / "dji_controller_test_mission.kmz"
        mission.to_kmz(str(kmz_file))
        
        # Verify KMZ file was created and has content
        assert kmz_file.exists()
        assert kmz_file.stat().st_size > 1000  # Should be substantial content
        
        # Also generate KML for inspection
        kml_file = test_dir / "dji_controller_test_mission.kml"
        xml_content = kml.to_xml()
        with open(kml_file, "w", encoding="utf-8") as f:
            f.write(xml_content)
        
        print(f"✅ Real-world test mission saved to: {kmz_file}")
        print(f"📁 KMZ file size: {kmz_file.stat().st_size} bytes")
        print(f"📄 KML file (for inspection): {kml_file}")
        print("🚁 Ready for DJI controller testing!")
        
        return kmz_file
        
    def test_enterprise_rtk_mission(self):
        """Test RTK mission for enterprise drones."""
        mission = (DroneTask("M350", "RTK Pilot")
                  .name("RTK Survey Mission")
                  .coordinate_system("RTK")
                  .speed(10.0)
                  .altitude(80.0)
                  .fly_to(37.7749, -122.4194)
                      .take_photo("rtk_point_1")
                  .fly_to(37.7750, -122.4195)
                      .take_photo("rtk_point_2"))
        
        kml = mission.build()
        assert kml.coordinate_system_param.coordinate_system == "WGS84"
        assert kml.coordinate_system_param.position_type == "RTKBaseStation"


class TestTaskBuilderChaining:
    """Test method chaining and fluent API."""
    
    def test_fluent_api_chaining(self):
        """Test that all methods return self for chaining."""
        result = (DroneTask("M30T", "Test Pilot")
                 .name("Chaining Test")
                 .speed(5.0)
                 .altitude(50.0)
                 .coordinate_system("GPS")
                 .return_home_on_signal_loss(True)
                 .fly_to(37.7749, -122.4194)
                 .take_photo("test")
                 .hover(1.0)
                 .gimbal_down(30)
                 .fly_to(37.7750, -122.4195))
        
        # Should be able to continue chaining
        kml = result.build()
        assert len(kml.waypoints) == 2
        
    def test_waypoint_method_returns(self):
        """Test that waypoint methods return WaypointBuilder."""
        task = DroneTask("M30T", "Test Pilot")
        waypoint_builder = task.fly_to(37.7749, -122.4194)
        
        # Should be able to chain waypoint actions
        chained = (waypoint_builder
                  .take_photo("test")
                  .hover(1.0)
                  .gimbal_front())
        
        # Should be able to continue with more waypoints
        kml = chained.fly_to(37.7750, -122.4195).build()
        assert len(kml.waypoints) == 2


class TestTaskBuilderTurnModes:
    """Test turn mode configuration functionality."""
    
    def test_global_turn_mode_setting(self):
        """Test setting global turn mode for all waypoints."""
        task = (DroneTask("M30T", "Test Pilot")
               .turn_mode("curve_and_pass")
               .fly_to(37.7749, -122.4194)
               .fly_to(37.7750, -122.4195))
        
        kml = task.build()
        # Global turn mode should be set in KML
        assert kml.global_turn_mode == "toPointAndPassWithContinuityCurvature"
        
        # Waypoints should use global turn param
        for waypoint in kml.waypoints:
            assert waypoint.use_global_turn_param == 1
            assert waypoint.turn_param is None
    
    def test_all_supported_global_turn_modes(self):
        """Test all supported global turn modes."""
        turn_modes = {
            "turn_at_point": "toPointAndStopWithDiscontinuityCurvature",
            "early_turn": "coordinateTurn", 
            "curve_and_stop": "toPointAndStopWithContinuityCurvature",
            "curve_and_pass": "toPointAndPassWithContinuityCurvature"
        }
        
        for mode_name, expected_value in turn_modes.items():
            task = (DroneTask("M30T", "Test Pilot")
                   .turn_mode(mode_name)
                   .fly_to(37.7749, -122.4194))
            
            kml = task.build()
            assert kml.global_turn_mode == expected_value, f"Failed for mode: {mode_name}"
    
    def test_invalid_global_turn_mode(self):
        """Test that invalid global turn modes raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            DroneTask("M30T", "Test Pilot").turn_mode("invalid_mode")
        
        assert "Invalid turn mode: invalid_mode" in str(exc_info.value)
        assert "turn_at_point" in str(exc_info.value)
        assert "early_turn" in str(exc_info.value)
        assert "curve_and_stop" in str(exc_info.value)
        assert "curve_and_pass" in str(exc_info.value)
    
    def test_per_waypoint_turn_mode_override(self):
        """Test setting turn mode for individual waypoints."""
        task = (DroneTask("M30T", "Test Pilot")
               .turn_mode("curve_and_pass")  # Global setting
               .fly_to(37.7749, -122.4194)
                   .turn_mode("turn_at_point")  # Override for this waypoint
               .fly_to(37.7750, -122.4195))    # Uses global setting
        
        kml = task.build()
        
        # Global turn mode should still be set
        assert kml.global_turn_mode == "toPointAndPassWithContinuityCurvature"
        
        # First waypoint should have override
        wp1 = kml.waypoints[0]
        assert wp1.use_global_turn_param == 0
        assert wp1.turn_param is not None
        assert wp1.turn_param.waypoint_turn_mode == "toPointAndStopWithDiscontinuityCurvature"
        
        # Second waypoint should use global
        wp2 = kml.waypoints[1]
        assert wp2.use_global_turn_param == 1
        assert wp2.turn_param is None
    
    def test_all_per_waypoint_turn_modes(self):
        """Test all supported per-waypoint turn modes."""
        turn_modes = {
            "turn_at_point": "toPointAndStopWithDiscontinuityCurvature",
            "early_turn": "coordinateTurn",
            "curve_and_stop": "toPointAndStopWithContinuityCurvature", 
            "curve_and_pass": "toPointAndPassWithContinuityCurvature"
        }
        
        for mode_name, expected_value in turn_modes.items():
            task = (DroneTask("M30T", "Test Pilot")
                   .fly_to(37.7749, -122.4194)
                       .turn_mode(mode_name))
            
            kml = task.build()
            waypoint = kml.waypoints[0]
            
            assert waypoint.use_global_turn_param == 0
            assert waypoint.turn_param is not None
            assert waypoint.turn_param.waypoint_turn_mode == expected_value, f"Failed for mode: {mode_name}"
    
    def test_early_turn_damping_distance(self):
        """Test that early_turn mode sets appropriate damping distance."""
        task = (DroneTask("M30T", "Test Pilot")
               .fly_to(37.7749, -122.4194)
                   .turn_mode("early_turn"))
        
        kml = task.build()
        waypoint = kml.waypoints[0]
        
        assert waypoint.turn_param.waypoint_turn_mode == "coordinateTurn"
        assert waypoint.turn_param.waypoint_turn_damping_dist == 0.2
    
    def test_non_early_turn_no_damping(self):
        """Test that non-early turn modes don't set damping distance."""
        modes_without_damping = ["turn_at_point", "curve_and_stop", "curve_and_pass"]
        
        for mode in modes_without_damping:
            task = (DroneTask("M30T", "Test Pilot")
                   .fly_to(37.7749, -122.4194)
                       .turn_mode(mode))
            
            kml = task.build()
            waypoint = kml.waypoints[0]
            
            assert waypoint.turn_param.waypoint_turn_damping_dist is None, f"Mode {mode} should not have damping"
    
    def test_default_turn_mode_reset(self):
        """Test that 'default' turn mode resets to global setting."""
        task = (DroneTask("M30T", "Test Pilot")
               .turn_mode("curve_and_pass")  # Set global
               .fly_to(37.7749, -122.4194)
                   .turn_mode("turn_at_point")  # Override
                   .turn_mode("default"))       # Reset to global
        
        kml = task.build()
        waypoint = kml.waypoints[0]
        
        # Should use global turn param
        assert waypoint.use_global_turn_param == 1
        assert waypoint.turn_param is None
    
    def test_invalid_per_waypoint_turn_mode(self):
        """Test that invalid per-waypoint turn modes raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            (DroneTask("M30T", "Test Pilot")
             .fly_to(37.7749, -122.4194)
             .turn_mode("invalid_waypoint_mode"))
        
        assert "Invalid turn mode: invalid_waypoint_mode" in str(exc_info.value)
    
    def test_mixed_turn_mode_configuration(self):
        """Test complex scenario with mixed global and per-waypoint turn modes."""
        task = (DroneTask("M30T", "Test Pilot")
               .turn_mode("curve_and_pass")  # Global default
               
               # Waypoint 1: Override to turn_at_point
               .fly_to(37.7749, -122.4194)
                   .turn_mode("turn_at_point")
                   .take_photo("stop_point")
               
               # Waypoint 2: Override to early_turn  
               .fly_to(37.7750, -122.4195)
                   .turn_mode("early_turn")
                   .hover(1.0)
               
               # Waypoint 3: Use global default
               .fly_to(37.7751, -122.4196)
                   .take_photo("flow_point")
               
               # Waypoint 4: Override then reset to default
               .fly_to(37.7752, -122.4197)
                   .turn_mode("curve_and_stop")
                   .turn_mode("default")
                   .take_photo("default_point"))
        
        kml = task.build()
        
        # Verify global setting
        assert kml.global_turn_mode == "toPointAndPassWithContinuityCurvature"
        
        # Verify each waypoint
        wp1, wp2, wp3, wp4 = kml.waypoints
        
        # WP1: turn_at_point override
        assert wp1.use_global_turn_param == 0
        assert wp1.turn_param.waypoint_turn_mode == "toPointAndStopWithDiscontinuityCurvature"
        assert wp1.turn_param.waypoint_turn_damping_dist is None
        
        # WP2: early_turn override with damping
        assert wp2.use_global_turn_param == 0
        assert wp2.turn_param.waypoint_turn_mode == "coordinateTurn"
        assert wp2.turn_param.waypoint_turn_damping_dist == 0.2
        
        # WP3: global default
        assert wp3.use_global_turn_param == 1
        assert wp3.turn_param is None
        
        # WP4: reset to default
        assert wp4.use_global_turn_param == 1
        assert wp4.turn_param is None
    
    def test_turn_mode_xml_serialization(self):
        """Test that turn modes are properly serialized in XML output."""
        task = (DroneTask("M30T", "Test Pilot")
               .turn_mode("early_turn")
               .fly_to(37.7749, -122.4194)
                   .turn_mode("curve_and_stop"))
        
        kml = task.build()
        xml_output = kml.to_xml()
        
        # Check global turn mode in XML
        assert "coordinateTurn" in xml_output
        
        # Check per-waypoint turn param in XML
        assert "toPointAndStopWithContinuityCurvature" in xml_output
        assert "useGlobalTurnParam>0" in xml_output  # Per-waypoint override
        # assert "waypointTurnDampingDist" in xml_output  # dji's global turn mode does not have damping distance. Meh.
    
    def test_turn_mode_kmz_generation(self):
        """Test that turn modes work correctly in KMZ file generation."""
        task = (DroneTask("M30T", "Test Pilot")
               .name("Turn Mode Test Mission")
               .turn_mode("curve_and_pass")
               .fly_to(37.7749, -122.4194)
                   .turn_mode("turn_at_point")
                   .take_photo("precise_stop")
               .fly_to(37.7750, -122.4195)
                   .turn_mode("early_turn")
                   .take_photo("smooth_approach")
               .fly_to(37.7751, -122.4196)
                   .take_photo("global_flow"))
        
        # Generate KMZ file
        test_dir = Path("test_output")
        test_dir.mkdir(exist_ok=True)
        
        kmz_file = test_dir / "turn_mode_test.kmz"
        task.to_kmz(str(kmz_file))
        
        # Verify file exists and has content
        assert kmz_file.exists()
        assert kmz_file.stat().st_size > 1000
        
        print(f"✅ Turn mode test KMZ generated: {kmz_file}")


class TestTaskBuilderPayload:
    """Test TaskBuilder payload configuration and compatibility."""
    
    def test_default_payload_assignment(self):
        """Test that default payloads are assigned correctly for each drone model."""
        # Test M30 series defaults
        m30_builder = DroneTask("M30")
        m30_builder.payload("M30").fly_to(37.7749, -122.4194)
        mission = m30_builder.build()
        
        # Verify default payload is M30
        payload_config = mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.M30
        
        # Test M30T thermal camera default
        m30t_builder = DroneTask("M30T")
        m30t_builder.payload("M30T").fly_to(37.7749, -122.4194)
        m30t_mission = m30t_builder.build()
        
        payload_config = m30t_mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.M30T
        
        # Test Mini 3 series defaults
        m3e_builder = DroneTask("M3E")
        m3e_builder.payload("M3E").fly_to(37.7749, -122.4194)
        m3e_mission = m3e_builder.build()
        
        payload_config = m3e_mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.M3E
    
    def test_explicit_payload_configuration(self):
        """Test explicit payload model configuration."""
        builder = DroneTask("M30")
        builder.payload("H20").fly_to(37.7749, -122.4194)  # Explicitly set H20 payload
        mission = builder.build()
        
        payload_config = mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.H20
    
    def test_payload_model_validation(self):
        """Test that invalid payload models raise appropriate errors."""
        builder = DroneTask("M30")
        
        # Test invalid string payload
        with pytest.raises(ValueError):
            builder.payload("InvalidPayload")
        
        # Test that builder can handle different payload configurations
        builder.payload("M30T").fly_to(37.7749, -122.4194)  # Valid alternative
        mission = builder.build()
        
        payload_config = mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.M30T
    
    def test_payload_string_mapping(self):
        """Test string-based payload mapping for convenience."""
        builder = DroneTask("M350")
        
        # Test string mapping to payload models
        builder.payload("H20").fly_to(37.7749, -122.4194)
        mission = builder.build()
        
        payload_config = mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.H20
        
        # Test another mapping
        builder2 = DroneTask("M300")
        builder2.payload("H20T").fly_to(37.7749, -122.4194)
        mission2 = builder2.build()
        
        payload_config2 = mission2.mission_config.payload_info
        assert payload_config2.payload_model == PayloadModel.H20T
    
    def test_payload_cross_compatibility(self):
        """Test payload compatibility across different drone models."""
        # M350 with H20 series payloads
        m350_builder = DroneTask("M350")
        m350_builder.payload("H20").fly_to(37.7749, -122.4194)
        m350_mission = m350_builder.build()
        
        payload_config = m350_mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.H20
        
        # M300 with H20T
        m300_builder = DroneTask("M300")
        m300_builder.payload("H20T").fly_to(37.7749, -122.4194)
        m300_mission = m300_builder.build()
        
        payload_config = m300_mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.H20T
        
        mini_builder = DroneTask("M3T")
        mini_builder.payload("M3T").fly_to(37.7749, -122.4194)
        mini_mission = mini_builder.build()
        
        payload_config = mini_mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.M3T
    
    def test_payload_configuration_persistence(self):
        """Test that payload configuration persists through builder operations."""
        builder = DroneTask("M30")
        builder.payload("M30T")
        
        # Add various operations
        builder.speed(5.0)
        builder.altitude(50.0)
        builder.fly_to(40.7128, -74.0060).take_photo()
        
        mission = builder.build()
        
        # Verify payload persisted
        payload_config = mission.mission_config.payload_info
        assert payload_config.payload_model == PayloadModel.M30T
    
    def test_multiple_drone_models_payload_defaults(self):
        """Test default payload assignment for all supported drone models."""
        expected_defaults = {
            "M30": PayloadModel.M30,
            "M30T": PayloadModel.M30T,
            "M3E": PayloadModel.M3E,
            "M3T": PayloadModel.M3T,
            "M3M": PayloadModel.M3M,
            "M3D": PayloadModel.M3D,
            "M3TD": PayloadModel.M3TD,
            "M350": PayloadModel.H20,  # Enterprise default
            "M300": PayloadModel.H20,  # Enterprise default
        }
        
        for drone_model, expected_payload in expected_defaults.items():
            builder = DroneTask(drone_model)
            builder.payload(expected_payload.name).fly_to(37.7749, -122.4194)
            mission = builder.build()
            
            payload_config = mission.mission_config.payload_info
            assert payload_config.payload_model == expected_payload, \
                f"Expected {expected_payload} for {drone_model}, got {payload_config.payload_model}"
    
    def test_payload_serialization_in_kmz(self):
        """Test that payload configuration is properly serialized in KMZ output."""
        import tempfile
        import zipfile
        
        builder = DroneTask("M30T")
        builder.payload("M30T")
        builder.fly_to(40.7128, -74.0060).take_photo()
        
        kml = builder.build()
        
        # Create KMZ and verify payload in XML
        with tempfile.NamedTemporaryFile(suffix='.kmz', delete=False) as temp_file:
            builder.to_kmz(temp_file.name)
            
            # Read and verify KMZ contents
            with zipfile.ZipFile(temp_file.name, 'r') as kmz:
                template_xml = kmz.read('wpmz/template.kml').decode('utf-8')
                
                # Verify payload model is in XML
                assert '53' in template_xml or 'payloadModel' in template_xml
                
                # Verify payload configuration elements exist
                assert 'payloadInfo' in template_xml or 'payload' in template_xml
        
        # Clean up
        import os
        os.unlink(temp_file.name)


class TestTaskBuilderHeading:
    """Test TaskBuilder heading (drone yaw) functionality."""
    
    def test_heading_basic_functionality(self):
        """Test basic heading control at waypoints."""
        builder = DroneTask("M30T")
        builder.fly_to(40.7128, -74.0060).heading(90.0)  # Face East
        mission = builder.build()
        
        # Verify waypoint has action
        waypoint = mission.waypoints[0]
        assert waypoint.action_group is not None
        assert len(waypoint.action_group.actions) == 1
        
        # Verify action type and parameters
        action = waypoint.action_group.actions[0]
        assert hasattr(action, 'aircraft_heading')
        assert action.aircraft_heading == 90.0
        assert hasattr(action, 'direction')
        assert action.direction == 'clockwise'
    
    def test_heading_angle_validation(self):
        """Test heading angle validation within -180 to 180 range."""
        builder = DroneTask("M30T")
        waypoint_builder = builder.fly_to(40.7128, -74.0060)
        
        # Valid angles should work
        waypoint_builder.heading(0.0)     # North
        waypoint_builder.heading(90.0)    # East  
        waypoint_builder.heading(-90.0)   # West
        waypoint_builder.heading(180.0)   # South
        waypoint_builder.heading(-180.0)  # South (negative)
        
        # Invalid angles should raise ValueError
        with pytest.raises(ValueError, match="Heading angle must be between -180 and 180 degrees"):
            waypoint_builder.heading(181.0)
        
        with pytest.raises(ValueError, match="Heading angle must be between -180 and 180 degrees"):
            waypoint_builder.heading(-181.0)
        
        with pytest.raises(ValueError, match="Heading angle must be between -180 and 180 degrees"):
            waypoint_builder.heading(360.0)
    
    def test_heading_cardinal_directions(self):
        """Test heading for standard cardinal directions."""
        builder = DroneTask("M30T")
        
        # Test North
        builder.fly_to(40.7128, -74.0060).heading(0.0)
        
        # Test East  
        builder.fly_to(40.7130, -74.0058).heading(90.0)
        
        # Test South
        builder.fly_to(40.7132, -74.0056).heading(180.0)
        
        # Test West
        builder.fly_to(40.7134, -74.0054).heading(-90.0)
        
        mission = builder.build()
        
        # Verify all waypoints have heading actions
        expected_headings = [0.0, 90.0, 180.0, -90.0]
        for i, waypoint in enumerate(mission.waypoints):
            assert waypoint.action_group is not None
            action = waypoint.action_group.actions[0]
            assert action.aircraft_heading == expected_headings[i]
    
    def test_heading_with_other_actions(self):
        """Test heading combined with other waypoint actions."""
        builder = DroneTask("M30T")
        waypoint_builder = (builder.fly_to(40.7128, -74.0060)
            .heading(45.0)      # Face northeast
            .take_photo()       # Take photo
            .hover(2.0)         # Hover for 2 seconds
            .gimbal_down(30.0)) # Point gimbal down
        
        mission = builder.build()
        waypoint = mission.waypoints[0]
        
        # Should have 4 actions: heading, photo, hover, gimbal
        assert waypoint.action_group is not None
        assert len(waypoint.action_group.actions) == 4
        
        # Verify heading action is present with correct value
        heading_action = None
        for action in waypoint.action_group.actions:
            if hasattr(action, 'aircraft_heading'):
                heading_action = action
                break
        
        assert heading_action is not None
        assert heading_action.aircraft_heading == 45.0
    
    def test_heading_multiple_waypoints(self):
        """Test different headings across multiple waypoints."""
        builder = DroneTask("M30T")
        
        # Create mission with different headings at each waypoint
        (builder.fly_to(40.7128, -74.0060).heading(0.0)    # North
            .fly_to(40.7130, -74.0058).heading(90.0)       # East
            .fly_to(40.7132, -74.0056).heading(-135.0)     # Northwest
            .fly_to(40.7134, -74.0054).heading(45.0))      # Northeast
        
        mission = builder.build()
        
        expected_headings = [0.0, 90.0, -135.0, 45.0]
        
        for i, waypoint in enumerate(mission.waypoints):
            assert waypoint.action_group is not None
            
            # Find heading action
            heading_action = None
            for action in waypoint.action_group.actions:
                if hasattr(action, 'aircraft_heading'):
                    heading_action = action
                    break
            
            assert heading_action is not None, f"No heading action found for waypoint {i}"
            assert heading_action.aircraft_heading == expected_headings[i], \
                f"Expected heading {expected_headings[i]} for waypoint {i}, got {heading_action.aircraft_heading}"
    
    def test_heading_action_id_assignment(self):
        """Test that heading actions get proper action IDs assigned."""
        builder = DroneTask("M30T")
        (builder.fly_to(40.7128, -74.0060)
            .heading(90.0)
            .take_photo()
            .fly_to(40.7130, -74.0058)
            .heading(-90.0)
            .hover(1.0))
        
        mission = builder.build()
        
        # Verify action IDs are assigned sequentially across waypoints
        all_action_ids = []
        for waypoint in mission.waypoints:
            if waypoint.action_group:
                for action in waypoint.action_group.actions:
                    all_action_ids.append(action.action_id)
        
        # Action IDs should start from 0 and be sequential
        expected_ids = list(range(len(all_action_ids)))
        assert all_action_ids == expected_ids
    
    def test_heading_fluent_api_chaining(self):
        """Test that heading() properly supports fluent API chaining."""
        builder = DroneTask("M30T")
        
        # Test method chaining works and returns WaypointBuilder
        result = (builder.fly_to(40.7128, -74.0060)
                    .heading(90.0)
                    .take_photo()
                    .heading(180.0)  # Can set multiple headings
                    .hover(1.0))
        
        # Should return WaypointBuilder instance
        assert isinstance(result, WaypointBuilder)
        
        # Should be able to continue chaining
        final_result = result.build()
        assert isinstance(final_result, KML)
    
    def test_heading_edge_case_values(self):
        """Test heading with edge case angle values."""
        builder = DroneTask("M30T")
        waypoint_builder = builder.fly_to(40.7128, -74.0060)
        
        # Test boundary values
        waypoint_builder.heading(-180.0)  # Minimum valid
        waypoint_builder.heading(180.0)   # Maximum valid
        waypoint_builder.heading(0.0)     # Zero
        waypoint_builder.heading(-0.0)    # Negative zero
        
        # Test fractional degrees
        waypoint_builder.heading(45.5)
        waypoint_builder.heading(-123.7)
        
        mission = waypoint_builder.build()
        waypoint = mission.waypoints[0]
        
        # Should have all heading actions
        assert waypoint.action_group is not None
        assert len(waypoint.action_group.actions) == 6
