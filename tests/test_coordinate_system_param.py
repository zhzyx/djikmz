"""
Test cases for coordinate system parameter module.
"""

import pytest
from pydantic import ValidationError
from djikmz.model.coordinate_system_param import (
    StrEnum,
    CoordinateModeEnum,
    HeightModeEnum,
    PositionTypeEnum,
    CoordinateSystemParam
)


class TestStrEnum:
    """Test StrEnum base class."""
    
    def test_string_representation(self):
        """Test string representation of StrEnum."""
        class TestEnum(StrEnum):
            VALUE1 = "test_value"
            VALUE2 = "another_value"
        
        assert str(TestEnum.VALUE1) == "test_value"
        assert str(TestEnum.VALUE2) == "another_value"
    
    def test_enum_inheritance(self):
        """Test that StrEnum properly inherits from str and Enum."""
        from enum import Enum
        assert issubclass(StrEnum, str)
        assert issubclass(StrEnum, Enum)


class TestCoordinateModeEnum:
    """Test CoordinateModeEnum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert CoordinateModeEnum.WGS84 == "WGS84"
    
    def test_string_representation(self):
        """Test string representation."""
        assert str(CoordinateModeEnum.WGS84) == "WGS84"
    
    def test_enum_creation(self):
        """Test creating enum from string value."""
        coord_mode = CoordinateModeEnum("WGS84")
        assert coord_mode == CoordinateModeEnum.WGS84


class TestHeightModeEnum:
    """Test HeightModeEnum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert HeightModeEnum.EGM96 == "EGM96"
        assert HeightModeEnum.RELATIVE == "relativeToStartPoint"
        assert HeightModeEnum.AGL == "aboveGroundLevel"
        assert HeightModeEnum.REAL_TIME_FOLLOW_SURFACE == "realTimeFollowSurface"
    
    def test_string_representation(self):
        """Test string representation."""
        assert str(HeightModeEnum.EGM96) == "EGM96"
        assert str(HeightModeEnum.RELATIVE) == "relativeToStartPoint"
        assert str(HeightModeEnum.AGL) == "aboveGroundLevel"
        assert str(HeightModeEnum.REAL_TIME_FOLLOW_SURFACE) == "realTimeFollowSurface"
    
    def test_enum_creation(self):
        """Test creating enum from string values."""
        height_mode = HeightModeEnum("EGM96")
        assert height_mode == HeightModeEnum.EGM96
        
        height_mode = HeightModeEnum("relativeToStartPoint")
        assert height_mode == HeightModeEnum.RELATIVE


class TestPositionTypeEnum:
    """Test PositionTypeEnum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert PositionTypeEnum.GPS == "GPS"
        assert PositionTypeEnum.RTK == "RTKBaseStation"
        assert PositionTypeEnum.QIANXUN == "QianXun"
        assert PositionTypeEnum.CUSTOM == "Custom"
    
    def test_string_representation(self):
        """Test string representation."""
        assert str(PositionTypeEnum.GPS) == "GPS"
        assert str(PositionTypeEnum.RTK) == "RTKBaseStation"
        assert str(PositionTypeEnum.QIANXUN) == "QianXun"
        assert str(PositionTypeEnum.CUSTOM) == "Custom"
    
    def test_enum_creation(self):
        """Test creating enum from string values."""
        position_type = PositionTypeEnum("GPS")
        assert position_type == PositionTypeEnum.GPS
        
        position_type = PositionTypeEnum("RTKBaseStation")
        assert position_type == PositionTypeEnum.RTK


class TestCoordinateSystemParam:
    """Test CoordinateSystemParam class."""
    
    def test_creation_with_defaults(self):
        """Test creating CoordinateSystemParam with default values."""
        coord_param = CoordinateSystemParam()
        
        assert coord_param.coordinate_system == CoordinateModeEnum.WGS84
        assert coord_param.height_mode == HeightModeEnum.RELATIVE
        assert coord_param.position_type == PositionTypeEnum.GPS
    
    def test_creation_with_specific_values(self):
        """Test creating CoordinateSystemParam with specific values."""
        coord_param = CoordinateSystemParam(
            coordinate_system=CoordinateModeEnum.WGS84,
            height_mode=HeightModeEnum.EGM96,
            position_type=PositionTypeEnum.RTK
        )
        
        assert coord_param.coordinate_system == CoordinateModeEnum.WGS84
        assert coord_param.height_mode == HeightModeEnum.EGM96
        assert coord_param.position_type == PositionTypeEnum.RTK
    
    def test_creation_with_string_values(self):
        """Test creating CoordinateSystemParam with string enum values."""
        coord_param = CoordinateSystemParam(
            coordinate_system="WGS84",
            height_mode="aboveGroundLevel",
            position_type="QianXun"
        )
        
        assert coord_param.coordinate_system == CoordinateModeEnum.WGS84
        assert coord_param.height_mode == HeightModeEnum.AGL
        assert coord_param.position_type == PositionTypeEnum.QIANXUN
    
    def test_invalid_enum_values(self):
        """Test creating CoordinateSystemParam with invalid enum values."""
        with pytest.raises(ValidationError):
            CoordinateSystemParam(coordinate_system="INVALID_COORD")
        
        with pytest.raises(ValidationError):
            CoordinateSystemParam(height_mode="INVALID_HEIGHT")
        
        with pytest.raises(ValidationError):
            CoordinateSystemParam(position_type="INVALID_POSITION")
    
    def test_all_height_mode_combinations(self):
        """Test CoordinateSystemParam with all height mode combinations."""
        height_modes = [
            HeightModeEnum.EGM96,
            HeightModeEnum.RELATIVE,
            HeightModeEnum.AGL,
            HeightModeEnum.REAL_TIME_FOLLOW_SURFACE
        ]
        
        for height_mode in height_modes:
            coord_param = CoordinateSystemParam(height_mode=height_mode)
            assert coord_param.height_mode == height_mode
    
    def test_all_position_type_combinations(self):
        """Test CoordinateSystemParam with all position type combinations."""
        position_types = [
            PositionTypeEnum.GPS,
            PositionTypeEnum.RTK,
            PositionTypeEnum.QIANXUN,
            PositionTypeEnum.CUSTOM
        ]
        
        for position_type in position_types:
            coord_param = CoordinateSystemParam(position_type=position_type)
            assert coord_param.position_type == position_type
    
    def test_to_dict_default(self):
        """Test to_dict method with default values."""
        coord_param = CoordinateSystemParam()
        result = coord_param.to_dict()
        
        expected = {
            "wpml:coordinateMode": "WGS84",
            "wpml:heightMode": "relativeToStartPoint",
            "wpml:positioningType": "GPS"
        }
        assert result == expected
    
    def test_to_dict_custom_values(self):
        """Test to_dict method with custom values."""
        coord_param = CoordinateSystemParam(
            coordinate_system=CoordinateModeEnum.WGS84,
            height_mode=HeightModeEnum.EGM96,
            position_type=PositionTypeEnum.RTK
        )
        
        result = coord_param.to_dict()
        
        expected = {
            "wpml:coordinateMode": "WGS84",
            "wpml:heightMode": "EGM96",
            "wpml:positioningType": "RTKBaseStation"
        }
        assert result == expected
    
    def test_from_dict_with_wpml_prefix(self):
        """Test from_dict method with wpml prefixed keys."""
        data = {
            "wpml:coordinateMode": "WGS84",
            "wpml:heightMode": "EGM96",
            "wpml:positioningType": "RTKBaseStation"
        }
        
        coord_param = CoordinateSystemParam.from_dict(data)
        
        assert coord_param.coordinate_system == CoordinateModeEnum.WGS84
        assert coord_param.height_mode == HeightModeEnum.EGM96
        assert coord_param.position_type == PositionTypeEnum.RTK
    
    def test_from_dict_without_wpml_prefix(self):
        """Test from_dict method without wpml prefixed keys."""
        data = {
            "coordinateMode": "WGS84",
            "heightMode": "aboveGroundLevel",
            "positioningType": "QianXun"
        }
        
        coord_param = CoordinateSystemParam.from_dict(data)
        
        assert coord_param.coordinate_system == CoordinateModeEnum.WGS84
        assert coord_param.height_mode == HeightModeEnum.AGL
        assert coord_param.position_type == PositionTypeEnum.QIANXUN
    
    def test_from_dict_partial_data(self):
        """Test from_dict method with partial data (uses defaults)."""
        data = {
            "wpml:heightMode": "EGM96"
        }
        
        coord_param = CoordinateSystemParam.from_dict(data)
        
        # Should use defaults for missing fields
        assert coord_param.coordinate_system == CoordinateModeEnum.WGS84  # default
        assert coord_param.height_mode == HeightModeEnum.EGM96  # from data
        assert coord_param.position_type == PositionTypeEnum.GPS  # default
    
    def test_from_dict_empty_data(self):
        """Test from_dict method with empty data (uses all defaults)."""
        data = {}
        
        coord_param = CoordinateSystemParam.from_dict(data)
        
        assert coord_param.coordinate_system == CoordinateModeEnum.WGS84
        assert coord_param.height_mode == HeightModeEnum.RELATIVE
        assert coord_param.position_type == PositionTypeEnum.GPS
    
    def test_xml_roundtrip_default(self):
        """Test XML serialization roundtrip with default values."""
        original = CoordinateSystemParam()
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = CoordinateSystemParam.from_xml(f'<wpml:coordinateSystemParam>{xml_str}</wpml:coordinateSystemParam>')
        
        assert recreated.coordinate_system == original.coordinate_system
        assert recreated.height_mode == original.height_mode
        assert recreated.position_type == original.position_type
    
    def test_xml_roundtrip_custom_values(self):
        """Test XML serialization roundtrip with custom values."""
        original = CoordinateSystemParam(
            coordinate_system=CoordinateModeEnum.WGS84,
            height_mode=HeightModeEnum.REAL_TIME_FOLLOW_SURFACE,
            position_type=PositionTypeEnum.CUSTOM
        )
        
        # Convert to XML and back
        xml_str = original.to_xml()
        recreated = CoordinateSystemParam.from_xml(f'<wpml:coordinateSystemParam>{xml_str}</wpml:coordinateSystemParam>')
        
        assert recreated.coordinate_system == original.coordinate_system
        assert recreated.height_mode == original.height_mode
        assert recreated.position_type == original.position_type
    
    def test_xml_roundtrip_all_combinations(self):
        """Test XML serialization roundtrip with all enum combinations."""
        test_cases = [
            (CoordinateModeEnum.WGS84, HeightModeEnum.EGM96, PositionTypeEnum.GPS),
            (CoordinateModeEnum.WGS84, HeightModeEnum.RELATIVE, PositionTypeEnum.RTK),
            (CoordinateModeEnum.WGS84, HeightModeEnum.AGL, PositionTypeEnum.QIANXUN),
            (CoordinateModeEnum.WGS84, HeightModeEnum.REAL_TIME_FOLLOW_SURFACE, PositionTypeEnum.CUSTOM),
        ]
        
        for coord_mode, height_mode, position_type in test_cases:
            original = CoordinateSystemParam(
                coordinate_system=coord_mode,
                height_mode=height_mode,
                position_type=position_type
            )
            
            # Convert to XML and back
            xml_str = original.to_xml()
            recreated = CoordinateSystemParam.from_xml(f'<wpml:coordinateSystemParam>{xml_str}</wpml:coordinateSystemParam>')
            
            assert recreated.coordinate_system == original.coordinate_system
            assert recreated.height_mode == original.height_mode
            assert recreated.position_type == original.position_type
    
    def test_serialization_aliases(self):
        """Test that serialization aliases work correctly."""
        coord_param = CoordinateSystemParam(
            coordinate_system=CoordinateModeEnum.WGS84,
            height_mode=HeightModeEnum.EGM96,
            position_type=PositionTypeEnum.RTK
        )
        
        # Test model_dump with aliases
        data = coord_param.model_dump(by_alias=True)
        
        assert 'wpml:coordinateMode' in data
        assert 'wpml:heightMode' in data
        assert 'wpml:positioningType' in data
        
        # Original field names should not be present when using aliases
        assert 'coordinate_system' not in data
        assert 'height_mode' not in data
        assert 'position_type' not in data


class TestCoordinateSystemParamEdgeCases:
    """Test edge cases for CoordinateSystemParam."""
    
    def test_invalid_xml_handling(self):
        """Test handling of invalid XML."""
        with pytest.raises(ValueError, match="Invalid XML format"):
            CoordinateSystemParam.from_xml("invalid xml")
    
    def test_m3x_specific_feature(self):
        """Test M3x specific real-time follow surface feature."""
        coord_param = CoordinateSystemParam(
            height_mode=HeightModeEnum.REAL_TIME_FOLLOW_SURFACE
        )
        
        assert coord_param.height_mode == HeightModeEnum.REAL_TIME_FOLLOW_SURFACE
        assert str(coord_param.height_mode) == "realTimeFollowSurface"
    
    def test_rtk_positioning_type(self):
        """Test RTK positioning type functionality."""
        coord_param = CoordinateSystemParam(
            position_type=PositionTypeEnum.RTK
        )
        
        assert coord_param.position_type == PositionTypeEnum.RTK
        assert str(coord_param.position_type) == "RTKBaseStation"
    
    def test_qianxun_positioning_type(self):
        """Test QianXun positioning type functionality."""
        coord_param = CoordinateSystemParam(
            position_type=PositionTypeEnum.QIANXUN
        )
        
        assert coord_param.position_type == PositionTypeEnum.QIANXUN
        assert str(coord_param.position_type) == "QianXun"
    
    def test_coordinate_system_consistency(self):
        """Test that only WGS84 coordinate system is supported."""
        # Currently only WGS84 is supported
        coord_param = CoordinateSystemParam()
        assert coord_param.coordinate_system == CoordinateModeEnum.WGS84
        
        # Test explicit WGS84 setting
        coord_param = CoordinateSystemParam(coordinate_system=CoordinateModeEnum.WGS84)
        assert coord_param.coordinate_system == CoordinateModeEnum.WGS84
    
    def test_field_descriptions(self):
        """Test that field descriptions are properly set."""
        model_fields = CoordinateSystemParam.model_fields
        
        assert "Coordinate system" in model_fields["coordinate_system"].description
        assert "WGS84" in model_fields["coordinate_system"].description
        assert "Height mode" in model_fields["height_mode"].description
        assert model_fields["position_type"].serialization_alias == "positioningType"
    
    def test_dict_roundtrip_consistency(self):
        """Test that dict roundtrip maintains consistency."""
        original = CoordinateSystemParam(
            coordinate_system=CoordinateModeEnum.WGS84,
            height_mode=HeightModeEnum.AGL,
            position_type=PositionTypeEnum.CUSTOM
        )
        
        # Convert to dict and back
        dict_data = original.to_dict()
        recreated = CoordinateSystemParam.from_dict(dict_data)
        
        assert recreated.coordinate_system == original.coordinate_system
        assert recreated.height_mode == original.height_mode
        assert recreated.position_type == original.position_type
        
        # Ensure the recreated dict is identical
        assert recreated.to_dict() == dict_data
