from pydantic import BaseModel, Field, model_serializer
from enum import Enum
import xmltodict

class StrEnum(str, Enum):
    """Base class for string enums."""
    def __str__(self):
        return self.value
    
class CoordinateModeEnum(StrEnum):
    WGS84 = "WGS84"
    
class HeightModeEnum(StrEnum):
    EGM96 = "EGM96"
    RELATIVE = "relativeToStartPoint"
    AGL = "aboveGroundLevel"
    REAL_TIME_FOLLOW_SURFACE = "realTimeFollowSurface" # only supported by M3x

class PositionTypeEnum(StrEnum):
    GPS = "GPS"
    RTK = "RTKBaseStation"
    QIANXUN = "QianXun"
    CUSTOM = "Custom"


class CoordinateSystemParam(BaseModel):
    "Coordinate system parameters for the waypoints"
    coordinate_system: CoordinateModeEnum = Field(
        default=CoordinateModeEnum.WGS84,
        serialization_alias="coordinateMode",
        description="Coordinate system used for the mission. Default is WGS84 (and the only support).")
    height_mode: HeightModeEnum = Field(
        default=HeightModeEnum.RELATIVE,
        serialization_alias="heightMode",
        description="Height mode used for the mission.")
    position_type: PositionTypeEnum = Field(
        default=PositionTypeEnum.GPS,
        serialization_alias="positioningType")
    # TODO: the following attributes are for mapping missions. Since we are focusing on
    # waypoint missions right now, they are not supported yet.
    # globalShootHeight         float           m used to calc photo spacing and GSD
    # surfaceFollowModeEnable   bool            enable surface follow mode 0 disabled, 1 enabled
    # surfaceRelativeHeight     float           m relative height to the surface

    def to_dict(self) -> dict:
        """Convert the CoordinateSystemParam to a dictionary."""
        # data = self.model_dump(by_alias=True, exclude_none=True)
        data = {field.serialization_alias or name: getattr(self, name) for name, field in type(self).model_fields.items() if getattr(self, name) is not None}
        for k, v in data.items():
            if isinstance(v, Enum):
                data[k] = str(v)
            elif isinstance(v, BaseModel):
                data[k] = v.model_dump(by_alias=True, exclude_none=True)
        return {f"wpml:{k}": v for k, v in data.items()}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CoordinateSystemParam':
        """Create a CoordinateSystemParam instance from a dictionary."""
        # Generate alias to field mapping automatically
        alias_to_field = {}
        for field_name, field_info in cls.model_fields.items():
            alias = field_info.serialization_alias or field_name
            alias_to_field[alias] = field_name
        
        clean_data = {}
        
        # Process each field, removing wpml: prefix and mapping aliases
        for key, value in data.items():
            clean_key = key.replace("wpml:", "")
            
            # Map alias to actual field name
            field_name = alias_to_field.get(clean_key, clean_key)
            clean_data[field_name] = value
        
        return cls(**clean_data)
    
    def to_xml(self) -> str:
        """Convert the CoordinateSystemParam to XML format."""
        xml_dict = self.to_dict()
        return xmltodict.unparse(xml_dict, pretty=True, full_document=False)
    
    @classmethod
    def from_xml(cls, xml_data: str) -> 'CoordinateSystemParam':
        """Create a CoordinateSystemParam instance from XML data."""
        try:
            data = xmltodict.parse(xml_data)
            coord_data = data.get("wpml:coordinateSystemParam", data)
        except:
            raise ValueError("Invalid XML format for coordinate system parameter")
        
        return cls.from_dict(coord_data)
    
    @model_serializer
    def serialize(self) -> dict:
        """Serialize the CoordinateSystemParam to a dictionary."""
        return self.to_dict()



