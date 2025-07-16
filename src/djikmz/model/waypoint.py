from pydantic import BaseModel, Field, field_validator, computed_field, model_serializer
from typing import List, Dict, Any, Optional, Union
import xmltodict

from .action_group import ActionGroup
from .heading_param import WaypointHeadingParam
from .turn_param import WaypointTurnParam

class Point(BaseModel):
    """Base class for geographic points."""
    
    latitude: float = Field(
        ...,
        description="Latitude in decimal degrees (-90 to 90)",
        ge=-90, le=90
    )
    longitude: float = Field(
        ...,
        description="Longitude in decimal degrees (-180 to 180)",
        ge=-180, le=180
    )
    def to_dict(self) -> Dict[str, Any]:
        """Convert the Point to a dictionary."""
        return {
            'coordinates': f"{self.longitude},{self.latitude}",
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Point':
        """Create a Point instance from a dictionary."""
        return cls(
            latitude=data.get('latitude', 0.0),
            longitude=data.get('longitude', 0.0)
        )
    def to_xml(self) -> str:
        """Convert the Point to XML format."""
        return xmltodict.unparse(self.to_dict(), pretty=True, full_document=False)
    @classmethod
    def from_xml(cls, xml_data: str) -> 'Point':
        """Create a Point instance from XML data."""
        data = xmltodict.parse(xml_data)
        coordinates = data.get('Point', {}).get('coordinates', '')
        if not coordinates:
            raise ValueError("Invalid XML data: 'coordinates' not found.")
        longitude, latitude = map(float, coordinates.split(','))
        return cls(latitude=latitude, longitude=longitude)
        

class Waypoint(BaseModel):
    latitude: float = Field(
        ...,
        description="Latitude in decimal degrees (-90 to 90)",
        ge= -90, le=90
    )  
    longitude: float = Field(
        ...,
        description="Longitude in decimal degrees (-180 to 180)",
        ge=-180, le=180
    )
    waypoint_id: int = Field(
        default=0,
        serialization_alias="index",
        ge=0,
        le=65535,
    )
    height: Optional[float] = Field(
        None,
        serialization_alias="height",
        description="Altitude in meters above takeoff point"
    )
    ellipsoid_height: Optional[float] = Field(
        None,
        serialization_alias="ellipsoidHeight",
        description="Ellipsoid height in meters"
    )
    use_global_height: int = Field(
        1,
        serialization_alias="useGlobalHeight",
        description="Use global height (0: No, 1: Yes)",
        ge=0, le=1
    )
    speed: Optional[float] = Field(
        None,
        serialization_alias="waypointSpeed",
        description="Flight speed in m/s"
    )
    use_global_speed: int = Field(
        1,
        serialization_alias="useGlobalSpeed",
        description="Use global speed (0: No, 1: Yes)",
        ge=0, le=1
    )
    heading_param: Optional[WaypointHeadingParam] = Field(
        None,
        serialization_alias="waypointHeadingParam",
        description="Heading parameter configuration for the waypoint"
    )
    # TODO change those to computed fields, based on corresponding parameters. 
    # e.g. if heading_param is None, use_global_heading_param should be 1, 
    # if heading_param is not None, use_global_heading_param should be 0.
    use_global_heading_param: int = Field(
        1,
        serialization_alias="useGlobalHeadingParam",
        description="Use global heading parameter (0: No, 1: Yes)",
        ge=0, le=1
    )
    turn_param: Optional[WaypointTurnParam] = Field(
        None,
        serialization_alias="waypointTurnParam",
        description="Turn parameter configuration for the waypoint"
    )
    use_global_turn_param: int = Field(
        1,
        serialization_alias="useGlobalTurnParam",
        description="Use global turn parameter (0: No, 1: Yes)",
        ge=0, le=1
    )
    use_straight_line: int = Field(
        1,
        serialization_alias="useStraightLine",
        description="Use straight line for waypoint (0: No, 1: Yes) 0/No means trajectory will be a curve.",
        ge=0, le=1
    )
    gimbal_pitch_angle: Optional[float] = Field(
        None,
        serialization_alias="gimbalPitchAngle",
        description="Gimbal pitch angle in degrees. Required if “wpml:gimbalPitchMode” is “usePointSetting”."
    )
    action_group: Optional[ActionGroup] = Field(
        None,
        serialization_alias="actionGroup",
        description="Action group associated with the waypoint"
    )

    @computed_field(alias="Point")
    def point(self) -> Point:
        """Return coordinates as a list [longitude, latitude]."""
        return Point(latitude=self.latitude, longitude=self.longitude)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Waypoint to a dictionary."""
        data = {field.serialization_alias or name: getattr(self, name) for name, field in type(self).model_fields.items() if getattr(self, name) is not None}
        # Remove the Point field from serialization, it will be added separately
        exclude=["latitude", "longitude", "point", "action_group", "heading_param", "turn_param"]
        for field in exclude:
            data.pop(field, None)
        data = {"wpml:" + k: v for k, v in data.items()}
        data['Point'] = self.point.to_dict()
        
        # Handle complex field serialization
        if self.action_group:
            data['wpml:actionGroup'] = self.action_group.to_dict()
        if self.heading_param:
            data['wpml:waypointHeadingParam'] = self.heading_param.to_dict()
        if self.turn_param:
            data['wpml:waypointTurnParam'] = self.turn_param.to_dict()

        return data

    def to_xml(self) -> str:
        """Convert the Waypoint to XML format."""
        return xmltodict.unparse(self.to_dict(), pretty=True, full_document=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Waypoint':
        """Create a Waypoint instance from a dictionary."""
        # Create a clean data dict for the constructor
        clean_data = {}
        
        # Handle coordinate extraction from Point
        if 'Point' in data:
            coordinates = data['Point']['coordinates'].split(',')
            clean_data['longitude'] = float(coordinates[0])
            clean_data['latitude'] = float(coordinates[1])
        
        alias_to_field = {}
        for field_name, field_info in cls.model_fields.items():
            alias = field_info.serialization_alias or field_name
            alias_to_field[alias] = field_name
        
        # Process each field, removing wpml: prefix and mapping aliases
        for key, value in data.items():
            if key == 'Point':
                continue  # Already handled above
                
            clean_key = key.replace("wpml:", "")
            
            # Map alias to actual field name
            field_name = alias_to_field.get(clean_key, clean_key)
            
            # Handle special cases for complex types
            if field_name == 'action_group' and value:
                clean_data[field_name] = ActionGroup.from_dict(value)
            elif field_name == 'heading_param' and value:
                clean_data[field_name] = WaypointHeadingParam.from_dict(value)
            elif field_name == 'turn_param' and value:
                clean_data[field_name] = WaypointTurnParam.from_dict(value)
            else:
                clean_data[field_name] = value
        
        return cls(**clean_data)
    
    @classmethod
    def from_xml(cls, xml_data: str) -> 'Waypoint':
        """Create a Waypoint instance from XML data."""
        data = xmltodict.parse(xml_data)
        waypoint_data = data.get('Placemark', {})        
        if not waypoint_data:
            raise ValueError("Invalid XML data: 'Placemark' not found.")
        return cls.from_dict(waypoint_data)
    
    @model_serializer
    def serialize(self) -> Dict[str, Any]:
        """Serialize the Waypoint to a dictionary."""
        return self.to_dict()