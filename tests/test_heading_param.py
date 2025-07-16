"""
Test cases for waypoint heading parameter module.
"""

import pytest
from pydantic import ValidationError
from djikmz.model.heading_param import (
    WaypointHeadingParam,
    WaypointHeadingMode,
    WaypointHeadingPathMode,
    WaypointPoiPoint
)


class TestWaypointPoiPoint:
    """Test WaypointPoiPoint class."""
    
    def test_creation(self):
        """Test creating POI point."""
        poi = WaypointPoiPoint(latitude=37.7749, longitude=-122.4194, altitude=100.0)
        assert poi.latitude == 37.7749
        assert poi.longitude == -122.4194
        assert poi.altitude == 100.0
    
    def test_default_altitude(self):
        """Test default altitude value."""
        poi = WaypointPoiPoint(latitude=37.7749, longitude=-122.4194)
        assert poi.altitude == 0.0
    
    def test_coordinate_validation(self):
        """Test coordinate validation."""
        # Valid coordinates
        WaypointPoiPoint(latitude=90, longitude=180)
        WaypointPoiPoint(latitude=-90, longitude=-180)
        
        # Invalid latitude
        with pytest.raises(ValidationError):
            WaypointPoiPoint(latitude=91, longitude=0)
        
        with pytest.raises(ValidationError):
            WaypointPoiPoint(latitude=-91, longitude=0)
        
        # Invalid longitude
        with pytest.raises(ValidationError):
            WaypointPoiPoint(latitude=0, longitude=181)
        
        with pytest.raises(ValidationError):
            WaypointPoiPoint(latitude=0, longitude=-181)
    
    def test_to_string(self):
        """Test converting to string format."""
        poi = WaypointPoiPoint(latitude=37.7749, longitude=-122.4194, altitude=100.0)
        assert poi.to_string() == "37.7749,-122.4194,100.0"
    
    def test_from_string(self):
        """Test creating from string format."""
        poi = WaypointPoiPoint.from_string("37.7749,-122.4194,100.0")
        assert poi.latitude == 37.7749
        assert poi.longitude == -122.4194
        assert poi.altitude == 100.0
    
    def test_from_string_invalid(self):
        """Test invalid string format."""
        with pytest.raises(ValueError):
            WaypointPoiPoint.from_string("37.7749,-122.4194")  # Missing altitude
        
        with pytest.raises(ValueError):
            WaypointPoiPoint.from_string("37.7749,-122.4194,100.0,extra")  # Too many parts


class TestWaypointHeadingParam:
    """Test WaypointHeadingParam class."""
    
    def test_follow_wayline_mode(self):
        """Test follow wayline mode."""
        param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.FOLLOW_WAYLINE,
            waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
        )
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.FOLLOW_WAYLINE
        assert param.waypoint_heading_path_mode == WaypointHeadingPathMode.FOLLOW_BAD_ARC
        assert param.waypoint_heading_angle is None
        assert param.waypoint_poi_point is None
    
    def test_manual_mode(self):
        """Test manual mode."""
        param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.MANUALLY,
            waypoint_heading_path_mode=WaypointHeadingPathMode.CLOCKWISE
        )
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.MANUALLY
        assert param.waypoint_heading_path_mode == WaypointHeadingPathMode.CLOCKWISE
    
    def test_fixed_mode(self):
        """Test fixed mode."""
        param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.FIXED,
            waypoint_heading_path_mode=WaypointHeadingPathMode.COUNTER_CLOCKWISE
        )
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.FIXED
        assert param.waypoint_heading_path_mode == WaypointHeadingPathMode.COUNTER_CLOCKWISE
    
    def test_smooth_transition_mode_with_angle(self):
        """Test smooth transition mode with required angle."""
        param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.SMOOTH_TRANSITION,
            waypoint_heading_angle=45.0,
            waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
        )
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.SMOOTH_TRANSITION
        assert param.waypoint_heading_angle == 45.0
    
    def test_smooth_transition_mode_missing_angle(self):
        """Test smooth transition mode fails without angle."""
        with pytest.raises(ValidationError, match="waypointHeadingAngle is required"):
            WaypointHeadingParam(
                waypoint_heading_mode=WaypointHeadingMode.SMOOTH_TRANSITION,
                waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
            )
    
    def test_toward_poi_mode_with_poi(self):
        """Test toward POI mode with required POI point."""
        poi = WaypointPoiPoint(latitude=37.7749, longitude=-122.4194)
        param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.TOWARD_POI,
            waypoint_poi_point=poi,
            waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
        )
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.TOWARD_POI
        assert param.waypoint_poi_point == poi
    
    def test_toward_poi_mode_missing_poi(self):
        """Test toward POI mode fails without POI point."""
        with pytest.raises(ValidationError, match="waypointPoiPoint is required"):
            WaypointHeadingParam(
                waypoint_heading_mode=WaypointHeadingMode.TOWARD_POI,
                waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
            )
    
    def test_string_enum_conversion(self):
        """Test string to enum conversion."""
        param = WaypointHeadingParam(
            waypoint_heading_mode="followWayline",
            waypoint_heading_path_mode="clockwise"
        )
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.FOLLOW_WAYLINE
        assert param.waypoint_heading_path_mode == WaypointHeadingPathMode.CLOCKWISE
    
    def test_invalid_heading_mode(self):
        """Test invalid heading mode."""
        with pytest.raises(ValidationError, match="Invalid waypoint heading mode"):
            WaypointHeadingParam(
                waypoint_heading_mode="invalidMode",
                waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
            )
    
    def test_invalid_path_mode(self):
        """Test invalid path mode."""
        with pytest.raises(ValidationError, match="Invalid waypoint heading path mode"):
            WaypointHeadingParam(
                waypoint_heading_mode=WaypointHeadingMode.FOLLOW_WAYLINE,
                waypoint_heading_path_mode="invalidPath"
            )
    
    def test_heading_angle_validation(self):
        """Test heading angle range validation."""
        # Valid angles
        WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.SMOOTH_TRANSITION,
            waypoint_heading_angle=180.0,
            waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
        )
        
        WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.SMOOTH_TRANSITION,
            waypoint_heading_angle=-180.0,
            waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
        )
        
        # Invalid angles
        with pytest.raises(ValidationError):
            WaypointHeadingParam(
                waypoint_heading_mode=WaypointHeadingMode.SMOOTH_TRANSITION,
                waypoint_heading_angle=181.0,
                waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
            )
        
        with pytest.raises(ValidationError):
            WaypointHeadingParam(
                waypoint_heading_mode=WaypointHeadingMode.SMOOTH_TRANSITION,
                waypoint_heading_angle=-181.0,
                waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
            )


class TestWaypointHeadingParamSerialization:
    """Test serialization/deserialization methods."""
    
    def test_to_dict_basic(self):
        """Test basic to_dict functionality."""
        param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.FOLLOW_WAYLINE,
            waypoint_heading_path_mode=WaypointHeadingPathMode.CLOCKWISE
        )
        
        result = param.to_dict()
        expected = {
            "wpml:waypointHeadingMode": "followWayline",
            "wpml:waypointHeadingPathMode": "clockwise"
        }
        
        assert result == expected
    
    def test_to_dict_with_angle(self):
        """Test to_dict with heading angle."""
        param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.SMOOTH_TRANSITION,
            waypoint_heading_angle=45.0,
            waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
        )
        
        result = param.to_dict()
        expected = {
            "wpml:waypointHeadingMode": "smoothTransition",
            "wpml:waypointHeadingAngle": 45.0,
            "wpml:waypointHeadingPathMode": "followBadArc"
        }
        
        assert result == expected
    
    def test_to_dict_with_poi(self):
        """Test to_dict with POI point."""
        poi = WaypointPoiPoint(latitude=37.7749, longitude=-122.4194, altitude=100.0)
        param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.TOWARD_POI,
            waypoint_poi_point=poi,
            waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
        )
        
        result = param.to_dict()
        expected = {
            "wpml:waypointHeadingMode": "towardPOI",
            "wpml:waypointPoiPoint": "37.7749,-122.4194,100.0",
            "wpml:waypointHeadingPathMode": "followBadArc"
        }
        
        assert result == expected
    
    def test_from_dict_basic(self):
        """Test basic from_dict functionality."""
        data = {
            "wpml:waypointHeadingMode": "followWayline",
            "wpml:waypointHeadingPathMode": "clockwise"
        }
        
        param = WaypointHeadingParam.from_dict(data)
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.FOLLOW_WAYLINE
        assert param.waypoint_heading_path_mode == WaypointHeadingPathMode.CLOCKWISE
        assert param.waypoint_heading_angle is None
        assert param.waypoint_poi_point is None
    
    def test_from_dict_with_angle(self):
        """Test from_dict with heading angle."""
        data = {
            "wpml:waypointHeadingMode": "smoothTransition",
            "wpml:waypointHeadingAngle": "45.0",
            "wpml:waypointHeadingPathMode": "followBadArc"
        }
        
        param = WaypointHeadingParam.from_dict(data)
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.SMOOTH_TRANSITION
        assert param.waypoint_heading_angle == 45.0
        assert param.waypoint_heading_path_mode == WaypointHeadingPathMode.FOLLOW_BAD_ARC
    
    def test_from_dict_with_poi(self):
        """Test from_dict with POI point."""
        data = {
            "wpml:waypointHeadingMode": "towardPOI",
            "wpml:waypointPoiPoint": "37.7749,-122.4194,100.0",
            "wpml:waypointHeadingPathMode": "followBadArc"
        }
        
        param = WaypointHeadingParam.from_dict(data)
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.TOWARD_POI
        assert param.waypoint_poi_point.latitude == 37.7749
        assert param.waypoint_poi_point.longitude == -122.4194
        assert param.waypoint_poi_point.altitude == 100.0
        assert param.waypoint_heading_path_mode == WaypointHeadingPathMode.FOLLOW_BAD_ARC
    
    def test_from_dict_without_prefix(self):
        """Test from_dict with keys without wpml: prefix."""
        data = {
            "waypointHeadingMode": "manually",
            "waypointHeadingPathMode": "counterClockwise"
        }
        
        param = WaypointHeadingParam.from_dict(data)
        
        assert param.waypoint_heading_mode == WaypointHeadingMode.MANUALLY
        assert param.waypoint_heading_path_mode == WaypointHeadingPathMode.COUNTER_CLOCKWISE
    
    def test_xml_roundtrip_basic(self):
        """Test XML serialization roundtrip for basic case."""
        original = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.FOLLOW_WAYLINE,
            waypoint_heading_path_mode=WaypointHeadingPathMode.CLOCKWISE
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = WaypointHeadingParam.from_xml(xml_str)
        
        assert recreated.waypoint_heading_mode == original.waypoint_heading_mode
        assert recreated.waypoint_heading_path_mode == original.waypoint_heading_path_mode
        assert recreated.waypoint_heading_angle == original.waypoint_heading_angle
        assert recreated.waypoint_poi_point == original.waypoint_poi_point
    
    def test_xml_roundtrip_with_angle(self):
        """Test XML serialization roundtrip with angle."""
        original = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.SMOOTH_TRANSITION,
            waypoint_heading_angle=90.0,
            waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = WaypointHeadingParam.from_xml(xml_str)
        
        assert recreated.waypoint_heading_mode == original.waypoint_heading_mode
        assert recreated.waypoint_heading_angle == original.waypoint_heading_angle
        assert recreated.waypoint_heading_path_mode == original.waypoint_heading_path_mode
    
    def test_xml_roundtrip_with_poi(self):
        """Test XML serialization roundtrip with POI."""
        poi = WaypointPoiPoint(latitude=37.7749, longitude=-122.4194, altitude=50.0)
        original = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.TOWARD_POI,
            waypoint_poi_point=poi,
            waypoint_heading_path_mode=WaypointHeadingPathMode.COUNTER_CLOCKWISE
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = WaypointHeadingParam.from_xml(xml_str)
        
        assert recreated.waypoint_heading_mode == original.waypoint_heading_mode
        assert recreated.waypoint_poi_point.latitude == original.waypoint_poi_point.latitude
        assert recreated.waypoint_poi_point.longitude == original.waypoint_poi_point.longitude
        assert recreated.waypoint_poi_point.altitude == original.waypoint_poi_point.altitude
        assert recreated.waypoint_heading_path_mode == original.waypoint_heading_path_mode
    
    def test_str_representation(self):
        """Test string representation."""
        # Basic case
        param1 = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.FOLLOW_WAYLINE,
            waypoint_heading_path_mode=WaypointHeadingPathMode.CLOCKWISE
        )
        str_repr1 = str(param1)
        assert "followWayline" in str_repr1
        assert "clockwise" in str_repr1
        
        # With angle
        param2 = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.SMOOTH_TRANSITION,
            waypoint_heading_angle=45.0,
            waypoint_heading_path_mode=WaypointHeadingPathMode.FOLLOW_BAD_ARC
        )
        str_repr2 = str(param2)
        assert "smoothTransition" in str_repr2
        assert "45.0°" in str_repr2
        
        # With POI
        poi = WaypointPoiPoint(latitude=37.7749, longitude=-122.4194)
        param3 = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.TOWARD_POI,
            waypoint_poi_point=poi,
            waypoint_heading_path_mode=WaypointHeadingPathMode.COUNTER_CLOCKWISE
        )
        str_repr3 = str(param3)
        assert "towardPOI" in str_repr3
        assert "37.7749" in str_repr3
        assert "-122.4194" in str_repr3
