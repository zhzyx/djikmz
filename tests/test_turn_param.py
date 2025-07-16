"""
Test cases for waypoint turn parameter module.
"""

import pytest
from pydantic import ValidationError
from djikmz.model.turn_param import (
    WaypointTurnParam,
    WaypointTurnMode
)


class TestWaypointTurnMode:
    """Test WaypointTurnMode enum."""
    
    def test_turn_mode_values(self):
        """Test turn mode enum values."""
        assert WaypointTurnMode.COORDINATED_TURN == "coordinateTurn"
        assert WaypointTurnMode.TURN_AT_POINT == "toPointAndStopWithDiscontinuityCurvature"
        assert WaypointTurnMode.CURVED_TURN_WITH_STOP == "toPointAndStopWithContinuityCurvature"
        assert WaypointTurnMode.CURVED_TURN_WITHOUT_STOP == "toPointAndPassWithContinuityCurvature"
    
    def test_turn_mode_str(self):
        """Test turn mode string representation."""
        assert str(WaypointTurnMode.COORDINATED_TURN) == "coordinateTurn"
        assert str(WaypointTurnMode.TURN_AT_POINT) == "toPointAndStopWithDiscontinuityCurvature"


class TestWaypointTurnParam:
    """Test WaypointTurnParam class."""
    
    def test_COORDINATED_TURN_with_damping(self):
        """Test coordinate turn mode with damping distance."""
        param = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
            waypoint_turn_damping_dist=5.0
        )
        
        assert param.waypoint_turn_mode == WaypointTurnMode.COORDINATED_TURN
        assert param.waypoint_turn_damping_dist == 5.0
    
    def test_COORDINATED_TURN_missing_damping(self):
        """Test coordinate turn mode fails without damping distance."""
        with pytest.raises(ValidationError, match="waypointTurnDampingDist is required"):
            WaypointTurnParam(
                waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN
            )
    
    def test_pass_with_continuity_with_damping(self):
        """Test pass with continuity mode with damping distance."""
        param = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.CURVED_TURN_WITHOUT_STOP,
            waypoint_turn_damping_dist=3.0
        )
        
        assert param.waypoint_turn_mode == WaypointTurnMode.CURVED_TURN_WITHOUT_STOP
        assert param.waypoint_turn_damping_dist == 3.0
    
    def test_stop_modes_without_damping(self):
        """Test stop modes work without damping distance."""
        # Stop with discontinuity
        param1 = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.TURN_AT_POINT
        )
        assert param1.waypoint_turn_damping_dist is None
        
        # Stop with continuity
        param2 = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.CURVED_TURN_WITH_STOP
        )
        assert param2.waypoint_turn_damping_dist is None
    
    def test_stop_modes_with_optional_damping(self):
        """Test stop modes work with optional damping distance."""
        param = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.CURVED_TURN_WITH_STOP,
            waypoint_turn_damping_dist=2.5
        )
        
        assert param.waypoint_turn_mode == WaypointTurnMode.CURVED_TURN_WITH_STOP
        assert param.waypoint_turn_damping_dist == 2.5
    
    def test_invalid_turn_mode(self):
        """Test invalid turn mode."""
        with pytest.raises(ValidationError, match="Input should be"):
            WaypointTurnParam(
                waypoint_turn_mode="invalidMode"
            )
    
    def test_invalid_damping_distance(self):
        """Test invalid damping distance."""
        with pytest.raises(ValidationError):
            WaypointTurnParam(
                waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
                waypoint_turn_damping_dist=0  # Must be greater than 0
            )
        
        with pytest.raises(ValidationError):
            WaypointTurnParam(
                waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
                waypoint_turn_damping_dist=-1  # Must be greater than 0
            )
    
    def test_to_dict(self):
        """Test to_dict method."""
        param = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
            waypoint_turn_damping_dist=5.0
        )
        
        result = param.to_dict()
        expected = {
            "wpml:waypointTurnMode": "coordinateTurn",
            "wpml:waypointTurnDampingDist": 5.0
        }
        
        assert result == expected
    
    def test_to_dict_without_damping(self):
        """Test to_dict method without damping distance."""
        param = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.TURN_AT_POINT
        )
        
        result = param.to_dict()
        expected = {
            "wpml:waypointTurnMode": "toPointAndStopWithDiscontinuityCurvature"
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test from_dict method."""
        data = {
            "wpml:waypointTurnMode": "coordinateTurn",
            "wpml:waypointTurnDampingDist": "5.0"
        }
        
        param = WaypointTurnParam.from_dict(data)
        
        assert param.waypoint_turn_mode == WaypointTurnMode.COORDINATED_TURN
        assert param.waypoint_turn_damping_dist == 5.0
    
    def test_from_dict_without_damping(self):
        """Test from_dict method without damping distance."""
        data = {
            "wpml:waypointTurnMode": "toPointAndStopWithDiscontinuityCurvature"
        }
        
        param = WaypointTurnParam.from_dict(data)
        
        assert param.waypoint_turn_mode == WaypointTurnMode.TURN_AT_POINT
        assert param.waypoint_turn_damping_dist is None
    
    def test_xml_roundtrip(self):
        """Test XML serialization roundtrip."""
        original = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
            waypoint_turn_damping_dist=5.0
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = WaypointTurnParam.from_xml(f'<wpml:waypointTurnParam>{xml_str}</wpml:waypointTurnParam>')
        
        assert recreated.waypoint_turn_mode == original.waypoint_turn_mode
        assert recreated.waypoint_turn_damping_dist == original.waypoint_turn_damping_dist
    
    def test_xml_roundtrip_without_damping(self):
        """Test XML serialization roundtrip without damping."""
        original = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.TURN_AT_POINT
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = WaypointTurnParam.from_xml(f'<wpml:waypointTurnParam>{xml_str}</wpml:waypointTurnParam>')
        
        assert recreated.waypoint_turn_mode == original.waypoint_turn_mode
        assert recreated.waypoint_turn_damping_dist is None


class TestWaypointTurnParamFactoryMethods:
    """Test factory methods for WaypointTurnParam."""
    
    def test_create_coordinated_turn(self):
        """Test coordinate turn factory method."""
        param = WaypointTurnParam.create_coordinated_turn(5.0)
        
        assert param.waypoint_turn_mode == WaypointTurnMode.COORDINATED_TURN
        assert param.waypoint_turn_damping_dist == 5.0
    
    def test_create_turn_at_point(self):
        """Test turn at point factory method."""
        param = WaypointTurnParam.create_turn_at_point()
        
        assert param.waypoint_turn_mode == WaypointTurnMode.TURN_AT_POINT
        assert param.waypoint_turn_damping_dist is None
    
    def test_create_curved_turn_with_stop(self):
        """Test curved turn with stop factory method."""
        param = WaypointTurnParam.create_curved_turn_with_stop()
        
        assert param.waypoint_turn_mode == WaypointTurnMode.CURVED_TURN_WITH_STOP
        assert param.waypoint_turn_damping_dist is None

    def test_create_curved_turn_without_stop(self):
        """Test curved turn without stop factory method."""
        param = WaypointTurnParam.create_curved_turn_without_stop()

        assert param.waypoint_turn_mode == WaypointTurnMode.CURVED_TURN_WITHOUT_STOP
        assert param.waypoint_turn_damping_dist is None


class TestWaypointTurnParamEdgeCases:
    """Test edge cases for WaypointTurnParam."""
    
    def test_string_representation(self):
        """Test string representation."""
        param1 = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
            waypoint_turn_damping_dist=5.0
        )
        
        str_repr = str(param1)
        assert "coordinateTurn" in str_repr
        assert "5.0m" in str_repr
        
        param2 = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.TURN_AT_POINT
        )
        
        str_repr2 = str(param2)
        assert "toPointAndStopWithDiscontinuityCurvature" in str_repr2
        assert "damping_dist" not in str_repr2
    
    def test_turn_mode_validation_with_string(self):
        """Test turn mode validation with string input."""
        param = WaypointTurnParam(
            waypoint_turn_mode="toPointAndStopWithDiscontinuityCurvature"
        )
        
        assert param.waypoint_turn_mode == WaypointTurnMode.TURN_AT_POINT
    
    def test_from_dict_with_non_prefixed_keys(self):
        """Test from_dict with non-prefixed keys."""
        data = {
            "waypointTurnMode": "coordinateTurn",
            "waypointTurnDampingDist": 5.0
        }
        
        param = WaypointTurnParam.from_dict(data)
        
        assert param.waypoint_turn_mode == WaypointTurnMode.COORDINATED_TURN
        assert param.waypoint_turn_damping_dist == 5.0
