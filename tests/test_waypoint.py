"""
Test cases for waypoint module.
"""

import pytest
from pydantic import ValidationError
from djikmz.model.waypoint import Waypoint, Point
from djikmz.model.action_group import ActionGroup, ActionTrigger, TriggerType
from djikmz.model.heading_param import WaypointHeadingParam, WaypointHeadingMode, WaypointHeadingPathMode
from djikmz.model.turn_param import WaypointTurnParam, WaypointTurnMode
from djikmz.model.action.camera_actions import TakePhotoAction


class TestPoint:
    """Test Point class."""
    
    def test_point_creation(self):
        """Test creating a Point."""
        point = Point(latitude=37.7749, longitude=-122.4194)
        assert point.latitude == 37.7749
        assert point.longitude == -122.4194
    
    def test_point_coordinate_validation(self):
        """Test Point coordinate validation."""
        # Valid coordinates
        Point(latitude=90, longitude=180)
        Point(latitude=-90, longitude=-180)
        Point(latitude=0, longitude=0)
        
        # Invalid latitude
        with pytest.raises(ValidationError):
            Point(latitude=91, longitude=0)
        
        with pytest.raises(ValidationError):
            Point(latitude=-91, longitude=0)
        
        # Invalid longitude  
        with pytest.raises(ValidationError):
            Point(latitude=0, longitude=181)
        
        with pytest.raises(ValidationError):
            Point(latitude=0, longitude=-181)
    
    def test_point_to_dict(self):
        """Test Point to_dict method."""
        point = Point(latitude=37.7749, longitude=-122.4194)
        result = point.to_dict()
        expected = {
            'coordinates': '-122.4194,37.7749'
        }
        assert result == expected
    
    def test_point_from_dict(self):
        """Test Point from_dict method."""
        data = {
            'latitude': 37.7749,
            'longitude': -122.4194
        }
        point = Point.from_dict(data)
        assert point.latitude == 37.7749
        assert point.longitude == -122.4194
    
    def test_point_xml_roundtrip(self):
        """Test Point XML serialization roundtrip."""
        original = Point(latitude=37.7749, longitude=-122.4194)
        
        # Convert to XML and back
        xml_str = original.to_xml()
        xml_str = '<Point>' + xml_str + '</Point>'
        
        print(xml_str)
        recreated = Point.from_xml(xml_str)
        
        assert recreated.latitude == original.latitude
        assert recreated.longitude == original.longitude


class TestWaypoint:
    """Test Waypoint class."""
    
    def test_waypoint_creation_minimal(self):
        """Test creating a minimal waypoint."""
        waypoint = Waypoint(
            latitude=37.7749,
            longitude=-122.4194
        )
        
        assert waypoint.latitude == 37.7749
        assert waypoint.longitude == -122.4194
        assert waypoint.waypoint_id == 0
        assert waypoint.height is None
        assert waypoint.ellipsoid_height is None
        assert waypoint.use_global_height == 1
        assert waypoint.speed is None
        assert waypoint.use_global_speed == 1
        assert waypoint.use_global_heading_param == 1
        assert waypoint.use_global_turn_param == 1
        assert waypoint.use_straight_line == 1
        assert waypoint.gimbal_pitch_angle is None
        assert waypoint.action_group is None
    
    def test_waypoint_creation_full(self):
        """Test creating a waypoint with all parameters."""
        heading_param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.FOLLOW_WAYLINE,
            waypoint_heading_path_mode=WaypointHeadingPathMode.CLOCKWISE
        )
        
        action_group = ActionGroup(
            group_id=1,
            actions=[TakePhotoAction(action_id=1)]
        )
        
        waypoint = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            waypoint_id=5,
            height=100.0,
            ellipsoid_height=150.0,
            use_global_height=0,
            speed=10.0,
            use_global_speed=0,
            heading_param=heading_param,
            use_global_heading_param=0,
            use_global_turn_param=0,
            use_straight_line=0,
            gimbal_pitch_angle=-45.0,
            action_group=action_group
        )
        
        assert waypoint.latitude == 37.7749
        assert waypoint.longitude == -122.4194
        assert waypoint.waypoint_id == 5
        assert waypoint.height == 100.0
        assert waypoint.ellipsoid_height == 150.0
        assert waypoint.use_global_height == 0
        assert waypoint.speed == 10.0
        assert waypoint.use_global_speed == 0
        assert waypoint.heading_param == heading_param
        assert waypoint.use_global_heading_param == 0
        assert waypoint.use_global_turn_param == 0
        assert waypoint.use_straight_line == 0
        assert waypoint.gimbal_pitch_angle == -45.0
        assert waypoint.action_group == action_group
    
    def test_waypoint_coordinate_validation(self):
        """Test waypoint coordinate validation."""
        # Valid coordinates
        Waypoint(latitude=90, longitude=180)
        Waypoint(latitude=-90, longitude=-180)
        Waypoint(latitude=0, longitude=0)
        
        # Invalid latitude
        with pytest.raises(ValidationError):
            Waypoint(latitude=91, longitude=0)
        
        with pytest.raises(ValidationError):
            Waypoint(latitude=-91, longitude=0)
        
        # Invalid longitude
        with pytest.raises(ValidationError):
            Waypoint(latitude=0, longitude=181)
        
        with pytest.raises(ValidationError):
            Waypoint(latitude=0, longitude=-181)
    
    def test_waypoint_id_validation(self):
        """Test waypoint ID validation."""
        # Valid IDs
        Waypoint(latitude=0, longitude=0, waypoint_id=0)
        Waypoint(latitude=0, longitude=0, waypoint_id=65535)
        
        # Invalid IDs
        with pytest.raises(ValidationError):
            Waypoint(latitude=0, longitude=0, waypoint_id=-1)
        
        with pytest.raises(ValidationError):
            Waypoint(latitude=0, longitude=0, waypoint_id=65536)
    
    def test_binary_field_validation(self):
        """Test binary field validation (0 or 1)."""
        # Valid values
        waypoint = Waypoint(
            latitude=0, longitude=0,
            use_global_height=0,
            use_global_speed=1,
            use_global_heading_param=0,
            use_global_turn_param=1,
            use_straight_line=0
        )
        
        assert waypoint.use_global_height == 0
        assert waypoint.use_global_speed == 1
        assert waypoint.use_global_heading_param == 0
        assert waypoint.use_global_turn_param == 1
        assert waypoint.use_straight_line == 0
        
        # Invalid values
        with pytest.raises(ValidationError):
            Waypoint(latitude=0, longitude=0, use_global_height=2)
        
        with pytest.raises(ValidationError):
            Waypoint(latitude=0, longitude=0, use_global_speed=-1)
    
    def test_waypoint_point_computed_field(self):
        """Test the computed Point field."""
        waypoint = Waypoint(latitude=37.7749, longitude=-122.4194)
        point = waypoint.point
        
        assert isinstance(point, Point)
        assert point.latitude == waypoint.latitude
        assert point.longitude == waypoint.longitude
    
    def test_waypoint_to_dict_minimal(self):
        """Test waypoint to_dict with minimal data."""
        waypoint = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            waypoint_id=1
        )
        
        result = waypoint.to_dict()
        
        # Should have wpml: prefixed fields and Point
        assert 'wpml:index' in result
        assert result['wpml:index'] == 1
        assert 'Point' in result
        assert result['Point']['coordinates'] == '-122.4194,37.7749'
        assert 'wpml:useGlobalHeight' in result
        assert result['wpml:useGlobalHeight'] == 1
    
    def test_waypoint_to_dict_with_action_group(self):
        """Test waypoint to_dict with action group."""
        action_group = ActionGroup(
            group_id=1,
            actions=[TakePhotoAction(action_id=1)]
        )
        
        waypoint = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            action_group=action_group
        )
        
        result = waypoint.to_dict()
        
        assert 'wpml:actionGroup' in result
        assert isinstance(result['wpml:actionGroup'], dict)
    
    def test_waypoint_from_dict(self):
        """Test waypoint from_dict method."""
        data = {
            'wpml:index': 5,
            'wpml:height': 100.0,
            'wpml:useGlobalHeight': 0,
            'wpml:waypointSpeed': 10.0,
            'wpml:useGlobalSpeed': 0,
            'Point': {
                'coordinates': '-122.4194,37.7749'
            }
        }
        
        waypoint = Waypoint.from_dict(data)
        
        assert waypoint.latitude == 37.7749
        assert waypoint.longitude == -122.4194
        assert waypoint.waypoint_id == 5
        assert waypoint.height == 100.0
        assert waypoint.use_global_height == 0
        assert waypoint.speed == 10.0
        assert waypoint.use_global_speed == 0
    
    def test_waypoint_from_dict_with_action_group(self):
        """Test waypoint from_dict with action group."""
        action_group_data = {
            'wpml:actionGroupId': 1,
            'wpml:actionGroupStartIndex': 1,
            'wpml:actionGroupEndIndex': 1,
            'wpml:executionMode': 'sequential',
            'wpml:action': [{
                'wpml:actionId': 1,
                'wpml:actionActuatorFunc': 'takePhoto',
                'wpml:payloadPosition': 0,
                'wpml:fileSuffix': 'photo1'
            }],
            'wpml:actionTrigger': {
                'wpml:actionTriggerType': 'reachPoint'
            }
        }
        
        data = {
            'wpml:index': 1,
            'Point': {
                'coordinates': '-122.4194,37.7749'
            },
            'wpml:actionGroup': action_group_data
        }
        
        waypoint = Waypoint.from_dict(data)
        
        assert waypoint.latitude == 37.7749
        assert waypoint.longitude == -122.4194
        assert waypoint.waypoint_id == 1
        assert waypoint.action_group is not None
        assert waypoint.action_group.group_id == 1
    
    def test_waypoint_xml_roundtrip_minimal(self):
        """Test waypoint XML serialization roundtrip with minimal data."""
        original = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            waypoint_id=1
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        xml_str = '<Placemark>' + xml_str + '</Placemark>'
        recreated = Waypoint.from_xml(xml_str)
        
        assert recreated.latitude == original.latitude
        assert recreated.longitude == original.longitude
        assert recreated.waypoint_id == original.waypoint_id
    
    def test_waypoint_xml_roundtrip_full(self):
        """Test waypoint XML serialization roundtrip with full data."""
        action_group = ActionGroup(
            group_id=1,
            actions=[TakePhotoAction(action_id=1)]
        )
        
        original = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            waypoint_id=5,
            height=100.0,
            ellipsoid_height=150.0,
            use_global_height=0,
            speed=10.0,
            use_global_speed=0,
            use_straight_line=0,
            gimbal_pitch_angle=-30.0,
            action_group=action_group
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        xml_str = '<Placemark>' + xml_str + '</Placemark>'
        recreated = Waypoint.from_xml(xml_str)
        
        assert recreated.latitude == original.latitude
        assert recreated.longitude == original.longitude
        assert recreated.waypoint_id == original.waypoint_id
        assert recreated.height == original.height
        assert recreated.ellipsoid_height == original.ellipsoid_height
        assert recreated.use_global_height == original.use_global_height
        assert recreated.speed == original.speed
        assert recreated.use_global_speed == original.use_global_speed
        assert recreated.use_straight_line == original.use_straight_line
        assert recreated.gimbal_pitch_angle == original.gimbal_pitch_angle
        assert recreated.action_group.group_id == original.action_group.group_id



class TestWaypointEdgeCases:
    """Test edge cases for waypoint."""
    
    def test_waypoint_with_none_values(self):
        """Test waypoint creation with None values for optional fields."""
        waypoint = Waypoint(
            latitude=0,
            longitude=0,
            height=None,
            ellipsoid_height=None,
            speed=None,
            heading_param=None,
            turn_param=None,
            gimbal_pitch_angle=None,
            action_group=None
        )
        
        assert waypoint.height is None
        assert waypoint.ellipsoid_height is None
        assert waypoint.speed is None
        assert waypoint.heading_param is None
        assert waypoint.turn_param is None
        assert waypoint.gimbal_pitch_angle is None
        assert waypoint.action_group is None
    
    def test_waypoint_empty_action_group(self):
        """Test waypoint with no action group."""
        waypoint = Waypoint(
            latitude=0,
            longitude=0,
            action_group=None
        )
        
        assert waypoint.action_group is None
    
    def test_waypoint_single_action_group(self):
        """Test waypoint with a single action group."""
        action_group = ActionGroup(
            group_id=1,
            actions=[TakePhotoAction(action_id=1)]
        )
        
        waypoint = Waypoint(
            latitude=0,
            longitude=0,
            action_group=action_group
        )
        
        assert waypoint.action_group is not None
        assert waypoint.action_group.group_id == 1
    
    def test_invalid_xml_data(self):
        """Test handling of invalid XML data."""
        # Missing waypoint data
        with pytest.raises(ValueError, match="Invalid XML data"):
            Waypoint.from_xml("<root></root>")
        
        # Invalid XML structure
        with pytest.raises(Exception):  # Should raise some parsing error
            Waypoint.from_xml("invalid xml")
    
    def test_coordinates_at_boundaries(self):
        """Test coordinates at valid boundaries."""
        # Test all boundary combinations
        boundary_coords = [
            (90, 180),    # Northeast corner
            (90, -180),   # Northwest corner  
            (-90, 180),   # Southeast corner
            (-90, -180),  # Southwest corner
            (0, 0),       # Equator/Prime meridian
        ]
        
        for lat, lon in boundary_coords:
            waypoint = Waypoint(latitude=lat, longitude=lon)
            assert waypoint.latitude == lat
            assert waypoint.longitude == lon
    
    def test_serialization_aliases(self):
        """Test that serialization aliases work correctly."""
        waypoint = Waypoint(
            latitude=0,
            longitude=0,
            waypoint_id=5,
            height=100.0,
            ellipsoid_height=150.0,
            speed=10.0
        )
        
        # Test model_dump with aliases
        data = waypoint.model_dump(by_alias=True)
        
        assert 'wpml:index' in data  # waypoint_id -> index
        assert 'wpml:height' in data  # height -> height (no change)
        assert 'wpml:ellipsoidHeight' in data  # ellipsoid_height -> ellipsoidHeight
        assert 'wpml:waypointSpeed' in data  # speed -> waypointSpeed
        
        # Original field names should not be present when using aliases
        assert 'wpml:waypoint_id' not in data
        assert 'wpml:ellipsoid_height' not in data
        assert 'wpml:speed' not in data
    
    def test_waypoint_with_turn_param(self):
        """Test waypoint with turn parameter."""
        turn_param = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
            waypoint_turn_damping_dist=5.0
        )
        
        waypoint = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            turn_param=turn_param,
            use_global_turn_param=0
        )
        
        assert waypoint.turn_param == turn_param
        assert waypoint.use_global_turn_param == 0
    
    def test_waypoint_with_turn_param_to_dict(self):
        """Test waypoint to_dict with turn parameter."""
        turn_param = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
            waypoint_turn_damping_dist=5.0
        )
        
        waypoint = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            turn_param=turn_param,
            use_global_turn_param=0
        )
        
        result = waypoint.to_dict()
        
        assert 'wpml:waypointTurnParam' in result
        assert result['wpml:waypointTurnParam']['wpml:waypointTurnMode'] == 'coordinateTurn'
        assert result['wpml:waypointTurnParam']['wpml:waypointTurnDampingDist'] == 5.0
        assert result['wpml:useGlobalTurnParam'] == 0
    
    def test_waypoint_with_turn_param_from_dict(self):
        """Test waypoint from_dict with turn parameter."""
        data = {
            'wpml:index': 1,
            'Point': {
                'coordinates': '-122.4194,37.7749'
            },
            'wpml:waypointTurnParam': {
                'wpml:waypointTurnMode': 'coordinateTurn',
                'wpml:waypointTurnDampingDist': 5.0
            },
            'wpml:useGlobalTurnParam': 0
        }
        
        waypoint = Waypoint.from_dict(data)
        
        assert waypoint.latitude == 37.7749
        assert waypoint.longitude == -122.4194
        assert waypoint.turn_param is not None
        assert waypoint.turn_param.waypoint_turn_mode == WaypointTurnMode.COORDINATED_TURN
        assert waypoint.turn_param.waypoint_turn_damping_dist == 5.0
        assert waypoint.use_global_turn_param == 0
    
    def test_waypoint_with_turn_param_xml_roundtrip(self):
        """Test waypoint XML roundtrip with turn parameter."""
        turn_param = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.CURVED_TURN_WITHOUT_STOP,
            waypoint_turn_damping_dist=3.0
        )
        
        original = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            waypoint_id=1,
            turn_param=turn_param,
            use_global_turn_param=0
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        xml_str = '<Placemark>' + xml_str + '</Placemark>'
        recreated = Waypoint.from_xml(xml_str)
        
        assert recreated.latitude == original.latitude
        assert recreated.longitude == original.longitude
        assert recreated.waypoint_id == original.waypoint_id
        assert recreated.turn_param is not None
        assert recreated.turn_param.waypoint_turn_mode == original.turn_param.waypoint_turn_mode
        assert recreated.turn_param.waypoint_turn_damping_dist == original.turn_param.waypoint_turn_damping_dist
        assert recreated.use_global_turn_param == original.use_global_turn_param
    
    def test_waypoint_with_different_turn_modes(self):
        """Test waypoint with different turn parameter modes."""
        # Test coordinate turn
        turn_param1 = WaypointTurnParam.create_coordinated_turn(5.0)
        waypoint1 = Waypoint(
            latitude=0, longitude=0,
            turn_param=turn_param1
        )
        assert waypoint1.turn_param.waypoint_turn_mode == WaypointTurnMode.COORDINATED_TURN
        
        # Test stop with discontinuity  
        turn_param2 = WaypointTurnParam.create_turn_at_point()
        waypoint2 = Waypoint(
            latitude=0, longitude=0,
            turn_param=turn_param2
        )
        assert waypoint2.turn_param.waypoint_turn_mode == WaypointTurnMode.TURN_AT_POINT
        
        # Test stop with continuity
        turn_param3 = WaypointTurnParam.create_curved_turn_with_stop()
        waypoint3 = Waypoint(
            latitude=0, longitude=0,
            turn_param=turn_param3
        )
        assert waypoint3.turn_param.waypoint_turn_mode == WaypointTurnMode.CURVED_TURN_WITH_STOP 
        
        # Test pass with continuity
        turn_param4 = WaypointTurnParam.create_curved_turn_without_stop()
        waypoint4 = Waypoint(
            latitude=0, longitude=0,
            turn_param=turn_param4
        )
        assert waypoint4.turn_param.waypoint_turn_mode == WaypointTurnMode.CURVED_TURN_WITHOUT_STOP
    
    def test_waypoint_with_both_heading_and_turn_params(self):
        """Test waypoint with both heading and turn parameters."""
        heading_param = WaypointHeadingParam(
            waypoint_heading_mode=WaypointHeadingMode.FOLLOW_WAYLINE,
            waypoint_heading_path_mode=WaypointHeadingPathMode.CLOCKWISE
        )
        
        turn_param = WaypointTurnParam(
            waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
            waypoint_turn_damping_dist=5.0
        )
        
        waypoint = Waypoint(
            latitude=37.7749,
            longitude=-122.4194,
            heading_param=heading_param,
            turn_param=turn_param,
            use_global_heading_param=0,
            use_global_turn_param=0
        )
        
        assert waypoint.heading_param == heading_param
        assert waypoint.turn_param == turn_param
        assert waypoint.use_global_heading_param == 0
        assert waypoint.use_global_turn_param == 0
        
        # Test serialization
        result = waypoint.to_dict()
        assert 'wpml:waypointHeadingParam' in result
        assert 'wpml:waypointTurnParam' in result
        assert result['wpml:useGlobalHeadingParam'] == 0
        assert result['wpml:useGlobalTurnParam'] == 0
    
    def test_waypoint_turn_param_edge_cases(self):
        """Test edge cases for waypoint turn parameter."""
        # Test waypoint with None turn param
        waypoint = Waypoint(
            latitude=0,
            longitude=0,
            turn_param=None
        )
        assert waypoint.turn_param is None
        
        # Test waypoint with turn param but using global settings
        turn_param = WaypointTurnParam.create_turn_at_point()
        waypoint = Waypoint(
            latitude=0,
            longitude=0,
            turn_param=turn_param,
            use_global_turn_param=1  # Using global settings
        )
        assert waypoint.turn_param == turn_param
        assert waypoint.use_global_turn_param == 1
