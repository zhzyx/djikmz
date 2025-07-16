"""
Waypoint heading parameter module for DJI KMZ mission files.

This module provides classes for managing waypoint heading behavior,
including different heading modes and their specific parameters.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator, model_serializer
from enum import Enum


class WaypointHeadingMode(str, Enum):
    """Enumeration of waypoint heading modes."""
    
    FOLLOW_WAYLINE = "followWayline"
    """Along course direction. The nose of the aircraft follows the course direction to the next waypoint."""
    
    MANUALLY = "manually" 
    """The user can manually control the nose orientation of the aircraft during the flight to the next waypoint."""
    
    FIXED = "fixed"
    """The nose of the aircraft maintains the yaw angle of the aircraft to the next waypoint after the waypoint action has been performed."""
    
    SMOOTH_TRANSITION = "smoothTransition"
    """Customized. The target yaw angle for a waypoint is given by "wpml:waypointHeadingAngle" and transitions evenly to the target yaw angle of the next waypoint during the flight segment."""
    
    TOWARD_POI = "towardPOI"
    """The aircraft heading faces the point of interest."""
    
    def __str__(self):
        return self.value


class WaypointHeadingPathMode(str, Enum):
    """Enumeration of waypoint heading path modes (direction of rotation)."""
    
    CLOCKWISE = "clockwise"
    """Rotate clockwise to reach target heading."""
    
    COUNTER_CLOCKWISE = "counterClockwise"
    """Rotate counter-clockwise to reach target heading."""
    
    FOLLOW_BAD_ARC = "followBadArc"
    """Rotation of the aircraft yaw angle along the shortest path."""
    
    def __str__(self):
        return self.value


class WaypointPoiPoint(BaseModel):
    """Point of interest coordinates for towardPOI heading mode."""
    
    latitude: float = Field(
        description="POI latitude in decimal degrees",
        ge=-90,
        le=90
    )
    
    longitude: float = Field(
        description="POI longitude in decimal degrees", 
        ge=-180,
        le=180
    )
    
    altitude: float = Field(
        default=0.0,
        description="POI altitude in meters (currently not used for Z-direction orientation)"
    )
    
    def to_string(self) -> str:
        """Convert to comma-separated string format for XML."""
        return f"{self.latitude},{self.longitude},{self.altitude}"
    
    @classmethod
    def from_string(cls, poi_string: str) -> "WaypointPoiPoint":
        """Create from comma-separated string format."""
        parts = poi_string.split(',')
        if len(parts) != 3:
            raise ValueError("POI point string must be in format 'lat,lon,alt'")
        
        return cls(
            latitude=float(parts[0]),
            longitude=float(parts[1]), 
            altitude=float(parts[2])
        )


class WaypointHeadingParam(BaseModel):
    """
    Waypoint heading parameter configuration.
    
    This class manages aircraft heading behavior during waypoint navigation,
    supporting various heading modes with their specific requirements.
    """
    
    waypoint_heading_mode: WaypointHeadingMode|str = Field(
        default=WaypointHeadingMode.FOLLOW_WAYLINE,
        serialization_alias="waypointHeadingMode",
        description="Heading mode for the waypoint"
    )
    
    waypoint_heading_angle: Optional[float] = Field(
        default=None,
        serialization_alias="waypointHeadingAngle",
        description="Target yaw angle in degrees [-180, 180]",
        ge=-180,
        le=180
    )
    
    waypoint_poi_point: Optional[WaypointPoiPoint] = Field(
        default=None,
        serialization_alias="waypointPoiPoint", 
        description="Point of interest coordinates for towardPOI mode"
    )
    
    waypoint_heading_path_mode: WaypointHeadingPathMode|str = Field(
        default=WaypointHeadingPathMode.FOLLOW_BAD_ARC,
        serialization_alias="waypointHeadingPathMode",
        description="Direction of rotation for aircraft yaw angle"
    )
    
    @field_validator('waypoint_heading_mode')
    @classmethod
    def validate_heading_mode(cls, v: Union[WaypointHeadingMode, str]) -> WaypointHeadingMode:
        """Validate and convert heading mode."""

        if isinstance(v, str):
            try:
                return WaypointHeadingMode(v)
            except ValueError:
                raise ValueError(f"Invalid waypoint heading mode: {v}")
        return v
    
    @field_validator('waypoint_heading_path_mode')
    @classmethod
    def validate_path_mode(cls, v: Union[WaypointHeadingPathMode, str]) -> WaypointHeadingPathMode:
        """Validate and convert path mode."""
        if isinstance(v, str):
            try:
                return WaypointHeadingPathMode(v)
            except ValueError:
                raise ValueError(f"Invalid waypoint heading path mode: {v}")
        return v
     
    @model_validator(mode='after')
    def validate_mode_requirements(self) -> 'WaypointHeadingParam':
        """Validate that required fields are present for specific modes."""
        
        # smoothTransition mode requires waypointHeadingAngle
        if (self.waypoint_heading_mode == WaypointHeadingMode.SMOOTH_TRANSITION and 
            self.waypoint_heading_angle is None):
            raise ValueError(
                "waypointHeadingAngle is required when waypointHeadingMode is 'smoothTransition'"
            )
        
        # towardPOI mode requires waypointPoiPoint
        if (self.waypoint_heading_mode == WaypointHeadingMode.TOWARD_POI and 
            self.waypoint_poi_point is None):
            raise ValueError(
                "waypointPoiPoint is required when waypointHeadingMode is 'towardPOI'"
            )
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with XML-compatible format."""
        result = {
            f"wpml:{WaypointHeadingParam.model_fields['waypoint_heading_mode'].serialization_alias}": self.waypoint_heading_mode.value,
            f"wpml:{WaypointHeadingParam.model_fields['waypoint_heading_path_mode'].serialization_alias}": self.waypoint_heading_path_mode.value
        }
        
        if self.waypoint_heading_angle is not None:
            result[f"wpml:{WaypointHeadingParam.model_fields['waypoint_heading_angle'].serialization_alias}"] = self.waypoint_heading_angle
        
        if self.waypoint_poi_point is not None:
            result[f"wpml:{WaypointHeadingParam.model_fields['waypoint_poi_point'].serialization_alias}"] = self.waypoint_poi_point.to_string()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WaypointHeadingParam":
        """Create from dictionary with XML data."""
        # Handle both prefixed and non-prefixed keys
        clean_data = {}
        
        for key, value in data.items():
            clean_key = key.replace("wpml:", "")
            
            if clean_key == "waypointHeadingMode":
                clean_data["waypoint_heading_mode"] = value
            elif clean_key == "waypointHeadingAngle":
                clean_data["waypoint_heading_angle"] = float(value)
            elif clean_key == "waypointPoiPoint":
                clean_data["waypoint_poi_point"] = WaypointPoiPoint.from_string(str(value))
            elif clean_key == "waypointHeadingPathMode":
                clean_data["waypoint_heading_path_mode"] = value
        
        return cls(**clean_data)
    
    def to_xml(self) -> str:
        """Convert to XML string."""
        import xmltodict
        xml_dict = self.to_dict()
        return xmltodict.unparse(xml_dict, pretty=True, full_document=False)
    
    @classmethod
    def from_xml(cls, xml_data: str) -> "WaypointHeadingParam":
        """Create from XML string."""
        import xmltodict
        # Handle both cases: with and without root element
        try:
            # Try parsing as complete XML with root
            data = xmltodict.parse(xml_data)
            # Look for known root elements
            if "wpml:waypointHeadingParam" in data:
                param_data = data["wpml:waypointHeadingParam"]
            elif "wpml:globalWaypointHeadingParam" in data:
                param_data = data["wpml:globalWaypointHeadingParam"]
            else:
                # Assume the data itself is the parameter data
                param_data = data
        except:
            # If parsing fails, try parsing as fragment
            param_data = xmltodict.parse(f"<root>{xml_data}</root>")["root"]
        
        return cls.from_dict(param_data)
    
    def __str__(self) -> str:
        """String representation of heading parameter."""
        result = f"HeadingParam(mode={self.waypoint_heading_mode.value}"
        
        if self.waypoint_heading_angle is not None:
            result += f", angle={self.waypoint_heading_angle}°"
        
        if self.waypoint_poi_point is not None:
            result += f", poi=({self.waypoint_poi_point.latitude}, {self.waypoint_poi_point.longitude})"
        
        result += f", path={self.waypoint_heading_path_mode.value})"
        return result
    
    @model_serializer
    def serialize(self) -> Dict[str, Any]:
        """Serialize the heading parameter to a dictionary."""
        return self.to_dict()

