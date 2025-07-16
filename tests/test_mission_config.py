"""
Test cases for mission configuration module.
"""

import pytest
from pydantic import ValidationError
from djikmz.model.mission_config import (
    FlyToWaylineMode,
    FinishAction,
    RCLostAction,
    DroneModel,
    DroneInfo,
    PayloadModel,
    PayloadInfo,
    MissionConfig,
    MODEL_TO_VAL
)


class TestFlyToWaylineMode:
    """Test FlyToWaylineMode enum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert FlyToWaylineMode.SAFELY == "safely"
        assert FlyToWaylineMode.POINTTOPOINT == "pointToPoint"
    
    def test_string_representation(self):
        """Test string representation."""
        assert str(FlyToWaylineMode.SAFELY) == "safely"
        assert str(FlyToWaylineMode.POINTTOPOINT) == "pointToPoint"


class TestFinishAction:
    """Test FinishAction enum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert FinishAction.GO_HOME == "goHome"
        assert FinishAction.AUTOLAND == "autoLand"
        assert FinishAction.GOTO_FIRST_WAYPOINT == "gotoFirstWaypoint"
        assert FinishAction.NO_ACTION == "noAction"
    
    def test_string_representation(self):
        """Test string representation."""
        assert str(FinishAction.GO_HOME) == "goHome"
        assert str(FinishAction.AUTOLAND) == "autoLand"


class TestRCLostAction:
    """Test RCLostAction enum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert RCLostAction.CONTINUE == "goContinue"
        assert RCLostAction.HOVER == "handover"
        assert RCLostAction.GO_HOME == "goBack"
        assert RCLostAction.LAND == "landing"
    
    def test_string_representation(self):
        """Test string representation."""
        assert str(RCLostAction.CONTINUE) == "goContinue"
        assert str(RCLostAction.HOVER) == "handover"


class TestDroneModel:
    """Test DroneModel enum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert DroneModel.M350 == "M350"
        assert DroneModel.M300 == "M300"
        assert DroneModel.M30 == "M30"
        assert DroneModel.M30T == "M30T"
    
    def test_model_to_val_mapping(self):
        """Test MODEL_TO_VAL mapping."""
        assert MODEL_TO_VAL[DroneModel.M350] == [89, None]
        assert MODEL_TO_VAL[DroneModel.M300] == [60, None]
        assert MODEL_TO_VAL[DroneModel.M30] == [67, 0]
        assert MODEL_TO_VAL[DroneModel.M30T] == [67, 1]


class TestPayloadModel:
    """Test PayloadModel enum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert PayloadModel.H20 == 42
        assert PayloadModel.M3M == 68
        assert PayloadModel.PSDK == 65534
    
    def test_string_representation(self):
        """Test string representation."""
        assert str(PayloadModel.H20) == "42"
        assert str(PayloadModel.M3M) == "68"


class TestDroneInfo:
    """Test DroneInfo class."""
    
    def test_creation_with_default(self):
        """Test creating DroneInfo with default values."""
        drone_info = DroneInfo()
        
        assert drone_info.drone_model == DroneModel.M350
        assert drone_info.drone_enum_value == 89
        assert drone_info.drone_sub_enum_value is None
    
    def test_creation_with_specific_model(self):
        """Test creating DroneInfo with specific drone model."""
        drone_info = DroneInfo(drone_model=DroneModel.M30T)
        
        assert drone_info.drone_model == DroneModel.M30T
        assert drone_info.drone_enum_value == 67
        assert drone_info.drone_sub_enum_value == 1
    
    def test_computed_fields(self):
        """Test computed fields for different drone models."""
        # Test M350 (no sub enum)
        drone_info = DroneInfo(drone_model=DroneModel.M350)
        assert drone_info.drone_enum_value == 89
        assert drone_info.drone_sub_enum_value is None
        
        # Test M30T (with sub enum)
        drone_info = DroneInfo(drone_model=DroneModel.M30T)
        assert drone_info.drone_enum_value == 67
        assert drone_info.drone_sub_enum_value == 1
    
    def test_to_dict(self):
        """Test to_dict method."""
        drone_info = DroneInfo(drone_model=DroneModel.M30T)
        result = drone_info.to_dict()
        
        expected = {
            "wpml:droneEnumValue": 67,
            "wpml:droneSubEnumValue": 1
        }
        assert result == expected
    
    def test_to_dict_no_sub_enum(self):
        """Test to_dict method for drone without sub enum."""
        drone_info = DroneInfo(drone_model=DroneModel.M350)
        result = drone_info.to_dict()
        
        expected = {
            "wpml:droneEnumValue": 89
        }
        assert result == expected
    
    def test_from_dict(self):
        """Test from_dict method."""
        data = {
            "wpml:droneEnumValue": 67,
            "wpml:droneSubEnumValue": 1
        }
        
        drone_info = DroneInfo.from_dict(data)
        
        assert drone_info.drone_model == DroneModel.M30T
        assert drone_info.drone_enum_value == 67
        assert drone_info.drone_sub_enum_value == 1
    
    def test_from_dict_no_sub_enum(self):
        """Test from_dict method without sub enum."""
        data = {
            "wpml:droneEnumValue": 89
        }
        
        drone_info = DroneInfo.from_dict(data)
        
        assert drone_info.drone_model == DroneModel.M350
        assert drone_info.drone_enum_value == 89
        assert drone_info.drone_sub_enum_value is None
    
    def test_from_dict_missing_enum_value(self):
        """Test from_dict with missing drone enum value."""
        data = {}
        
        with pytest.raises(ValueError, match="droneEnumValue is required"):
            DroneInfo.from_dict(data)
    
    def test_from_dict_unknown_drone(self):
        """Test from_dict with unknown drone model."""
        data = {
            "wpml:droneEnumValue": 999,
            "wpml:droneSubEnumValue": 999
        }
        
        with pytest.raises(ValueError, match="Unknown drone model"):
            DroneInfo.from_dict(data)
    
    def test_xml_roundtrip(self):
        """Test XML serialization roundtrip."""
        original = DroneInfo(drone_model=DroneModel.M30T)
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = DroneInfo.from_xml(f'<wpml:droneInfo>{xml_str}</wpml:droneInfo>')
        
        assert recreated.drone_model == original.drone_model
        assert recreated.drone_enum_value == original.drone_enum_value
        assert recreated.drone_sub_enum_value == original.drone_sub_enum_value


class TestPayloadInfo:
    """Test PayloadInfo class."""
    
    def test_creation_with_defaults(self):
        """Test creating PayloadInfo with default values."""
        payload_info = PayloadInfo()
        
        assert payload_info.payload_model == PayloadModel.M3M
        assert payload_info.position == 0
    
    def test_creation_with_specific_values(self):
        """Test creating PayloadInfo with specific values."""
        payload_info = PayloadInfo(
            payload_model=PayloadModel.H20T,
            position=1
        )
        
        assert payload_info.payload_model == PayloadModel.H20T
        assert payload_info.position == 1
    
    def test_to_dict(self):
        """Test to_dict method."""
        payload_info = PayloadInfo(
            payload_model=PayloadModel.H20T,
            position=1
        )
        
        result = payload_info.to_dict()
        
        expected = {
            "wpml:payloadEnumValue": 43,
            "wpml:payloadPositionIndex": 1
        }
        assert result == expected
    
    def test_from_dict(self):
        """Test from_dict method."""
        data = {
            "wpml:payloadEnumValue": 43,
            "wpml:payloadPositionIndex": 1
        }
        
        payload_info = PayloadInfo.from_dict(data)
        
        assert payload_info.payload_model == PayloadModel.H20T
        assert payload_info.position == 1
    
    def test_xml_roundtrip(self):
        """Test XML serialization roundtrip."""
        original = PayloadInfo(
            payload_model=PayloadModel.H20T,
            position=1
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = PayloadInfo.from_xml(f'<wpml:payloadInfo>{xml_str}</wpml:payloadInfo>')
        
        assert recreated.payload_model == original.payload_model
        assert recreated.position == original.position


class TestMissionConfig:
    """Test MissionConfig class."""
    
    def test_creation_with_defaults(self):
        """Test creating MissionConfig with default values."""
        config = MissionConfig()
        
        assert config.fly_to_wayline_mode == FlyToWaylineMode.SAFELY
        assert config.finish_action == FinishAction.GO_HOME
        assert config.rclost_action == RCLostAction.CONTINUE
        assert config.take_off_height == 1.2
        assert config.ref_take_off is None
        assert config.ref_take_off_altitude is None
        assert config.drone_info is None
        assert config.payload_info is None
    
    def test_creation_with_specific_values(self):
        """Test creating MissionConfig with specific values."""
        drone_info = DroneInfo(drone_model=DroneModel.M30T)
        payload_info = PayloadInfo(payload_model=PayloadModel.H20T)
        
        config = MissionConfig(
            fly_to_wayline_mode=FlyToWaylineMode.POINTTOPOINT,
            finish_action=FinishAction.AUTOLAND,
            rclost_action=RCLostAction.HOVER,
            take_off_height=50.0,
            drone_info=drone_info,
            payload_info=payload_info
        )
        
        assert config.fly_to_wayline_mode == FlyToWaylineMode.POINTTOPOINT
        assert config.finish_action == FinishAction.AUTOLAND
        assert config.rclost_action == RCLostAction.HOVER
        assert config.take_off_height == 50.0
        assert config.drone_info == drone_info
        assert config.payload_info == payload_info
    
    def test_computed_fields_continue(self):
        """Test computed fields when RC lost action is CONTINUE."""
        config = MissionConfig(rclost_action=RCLostAction.CONTINUE)
        
        assert config.exit_on_rc_lost == "goContinue"
        assert config.execute_rc_lost_action is None
    
    def test_computed_fields_hover(self):
        """Test computed fields when RC lost action is HOVER."""
        config = MissionConfig(rclost_action=RCLostAction.HOVER)
        
        assert config.exit_on_rc_lost == "executeLostAction"
        assert config.execute_rc_lost_action == "handover"
    
    def test_computed_fields_go_home(self):
        """Test computed fields when RC lost action is GO_HOME."""
        config = MissionConfig(rclost_action=RCLostAction.GO_HOME)
        
        assert config.exit_on_rc_lost == "executeLostAction"
        assert config.execute_rc_lost_action == "goBack"
    
    def test_computed_fields_land(self):
        """Test computed fields when RC lost action is LAND."""
        config = MissionConfig(rclost_action=RCLostAction.LAND)
        
        assert config.exit_on_rc_lost == "executeLostAction"
        assert config.execute_rc_lost_action == "landing"
    
    def test_take_off_height_validation(self):
        """Test take off height validation."""
        # Valid height
        config = MissionConfig(take_off_height=10.0)
        assert config.take_off_height == 10.0
        
        # Invalid height (too low)
        with pytest.raises(ValidationError):
            MissionConfig(take_off_height=1.0)
        
        # Invalid height (too high)
        with pytest.raises(ValidationError):
            MissionConfig(take_off_height=2000.0)
    
    def test_to_dict_minimal(self):
        """Test to_dict method with minimal configuration."""
        config = MissionConfig()
        result = config.to_dict()
        
        expected = {
            "wpml:flyToWaylineMode": "safely",
            "wpml:finishAction": "goHome",
            "wpml:exitOnRCLost": "goContinue",
            "wpml:takeOffSecurityHeight": 1.2
        }
        assert result == expected
    
    def test_to_dict_with_nested_objects(self):
        """Test to_dict method with nested objects."""
        drone_info = DroneInfo(drone_model=DroneModel.M30T)
        payload_info = PayloadInfo(payload_model=PayloadModel.H20T, position=1)
        
        config = MissionConfig(
            rclost_action=RCLostAction.HOVER,
            drone_info=drone_info,
            payload_info=payload_info
        )
        
        result = config.to_dict()
        
        assert "wpml:droneInfo" in result
        assert result["wpml:droneInfo"]["wpml:droneEnumValue"] == 67
        assert "wpml:payloadInfo" in result
        assert result["wpml:payloadInfo"]["wpml:payloadEnumValue"] == 43
        assert result["wpml:exitOnRCLost"] == "executeLostAction"
        assert result["wpml:executeRCLostAction"] == "handover"
    
    def test_from_dict_continue_action(self):
        """Test from_dict method with continue RC lost action."""
        data = {
            "wpml:flyToWaylineMode": "pointToPoint",
            "wpml:finishAction": "autoLand",
            "wpml:exitOnRCLost": "goContinue",
            "wpml:takeOffSecurityHeight": 25.0
        }
        
        config = MissionConfig.from_dict(data)
        
        assert config.fly_to_wayline_mode == FlyToWaylineMode.POINTTOPOINT
        assert config.finish_action == FinishAction.AUTOLAND
        assert config.rclost_action == RCLostAction.CONTINUE
        assert config.take_off_height == 25.0
    
    def test_from_dict_execute_lost_action(self):
        """Test from_dict method with execute lost action."""
        data = {
            "wpml:flyToWaylineMode": "safely",
            "wpml:finishAction": "goHome",
            "wpml:exitOnRCLost": "executeLostAction",
            "wpml:executeRCLostAction": "goBack",
            "wpml:takeOffSecurityHeight": 10.0
        }
        
        config = MissionConfig.from_dict(data)
        
        assert config.fly_to_wayline_mode == FlyToWaylineMode.SAFELY
        assert config.finish_action == FinishAction.GO_HOME
        assert config.rclost_action == RCLostAction.GO_HOME
        assert config.take_off_height == 10.0
    
    def test_from_dict_with_nested_objects(self):
        """Test from_dict method with nested objects."""
        data = {
            "wpml:flyToWaylineMode": "safely",
            "wpml:finishAction": "goHome",
            "wpml:exitOnRCLost": "goContinue",
            "wpml:takeOffSecurityHeight": 1.2,
            "wpml:droneInfo": {
                "droneEnumValue": 67,
                "droneSubEnumValue": 1
            },
            "wpml:payloadInfo": {
                "wpml:payloadEnumValue": 43,
                "wpml:payloadPositionIndex": 1
            }
        }
        
        config = MissionConfig.from_dict(data)
        
        assert config.drone_info is not None
        assert config.drone_info.drone_model == DroneModel.M30T
        assert config.payload_info is not None
        assert config.payload_info.payload_model == PayloadModel.H20T
        assert config.payload_info.position == 1
    
    def test_from_dict_unknown_execute_action(self):
        """Test from_dict with unknown executeRCLostAction."""
        data = {
            "wpml:exitOnRCLost": "executeLostAction",
            "wpml:executeRCLostAction": "unknownAction"
        }
        
        config = MissionConfig.from_dict(data)
        
        # Should fall back to CONTINUE
        assert config.rclost_action == RCLostAction.CONTINUE
    
    def test_xml_roundtrip_minimal(self):
        """Test XML serialization roundtrip with minimal configuration."""
        original = MissionConfig()
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = MissionConfig.from_xml(f'<wpml:missionConfig>{xml_str}</wpml:missionConfig>')
        
        assert recreated.fly_to_wayline_mode == original.fly_to_wayline_mode
        assert recreated.finish_action == original.finish_action
        assert recreated.rclost_action == original.rclost_action
        assert recreated.take_off_height == original.take_off_height
    
    def test_xml_roundtrip_full(self):
        """Test XML serialization roundtrip with full configuration."""
        drone_info = DroneInfo(drone_model=DroneModel.M30T)
        payload_info = PayloadInfo(payload_model=PayloadModel.H20T, position=1)
        
        original = MissionConfig(
            fly_to_wayline_mode=FlyToWaylineMode.POINTTOPOINT,
            finish_action=FinishAction.AUTOLAND,
            rclost_action=RCLostAction.HOVER,
            take_off_height=50.0,
            drone_info=drone_info,
            payload_info=payload_info
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = MissionConfig.from_xml(f'<wpml:missionConfig>{xml_str}</wpml:missionConfig>')
        
        assert recreated.fly_to_wayline_mode == original.fly_to_wayline_mode
        assert recreated.finish_action == original.finish_action
        assert recreated.rclost_action == original.rclost_action
        assert recreated.take_off_height == original.take_off_height
        assert recreated.drone_info.drone_model == original.drone_info.drone_model
        assert recreated.payload_info.payload_model == original.payload_info.payload_model
        assert recreated.payload_info.position == original.payload_info.position


class TestMissionConfigEdgeCases:
    """Test edge cases for MissionConfig."""
    
    def test_placeholder_fields_excluded(self):
        """Test that placeholder fields are excluded from serialization."""
        config = MissionConfig()
        result = config.to_dict()
        
        # Placeholder fields should not appear in serialized output
        assert "wpml:refTakeOffPoint" not in result
        assert "wpml:takeOffRefPointAGLHeight" not in result
        assert "refTakeOffPoint" not in result
        assert "takeOffRefPointAGLHeight" not in result
    
    def test_rclost_action_excluded_from_serialization(self):
        """Test that rclost_action field is excluded from serialization."""
        config = MissionConfig(rclost_action=RCLostAction.HOVER)
        result = config.to_dict()
        
        # rclost_action should not appear, only computed fields
        assert "wpml:rclost_action" not in result
        assert "rclost_action" not in result
        assert "wpml:exitOnRCLost" in result
        assert "wpml:executeRCLostAction" in result
    
    def test_invalid_xml_handling(self):
        """Test handling of invalid XML."""
        with pytest.raises(ValueError, match="Invalid XML format"):
            MissionConfig.from_xml("invalid xml")
    
    def test_all_rc_lost_action_mappings(self):
        """Test all RC lost action enum mappings."""
        test_cases = [
            (RCLostAction.CONTINUE, "goContinue", None),
            (RCLostAction.HOVER, "executeLostAction", "handover"),
            (RCLostAction.GO_HOME, "executeLostAction", "goBack"),
            (RCLostAction.LAND, "executeLostAction", "landing")
        ]
        
        for action, expected_exit, expected_execute in test_cases:
            config = MissionConfig(rclost_action=action)
            assert config.exit_on_rc_lost == expected_exit
            assert config.execute_rc_lost_action == expected_execute
