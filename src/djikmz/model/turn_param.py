"""
Waypoint turn parameter module for DJI KMZ mission files.

This module provides classes for managing waypoint turn behavior,
including different turn modes and their specific parameters.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
import xmltodict

class StrEnum(str, Enum):
    """Base class for string enums."""
    def __str__(self):
        return self.value


class WaypointTurnMode(StrEnum):
    """Enumeration of waypoint turn modes."""
    COORDINATED_TURN = "coordinateTurn" # DJI use coordinateTurn without 'd'
    TURN_AT_POINT = "toPointAndStopWithDiscontinuityCurvature"
    CURVED_TURN_WITHOUT_STOP = "toPointAndPassWithContinuityCurvature"
    CURVED_TURN_WITH_STOP = "toPointAndStopWithContinuityCurvature"


class WaypointTurnParam(BaseModel):
    """
    Waypoint turn parameter configuration.
    
    This class manages aircraft turn behavior at waypoints,
    supporting various turn modes with their specific requirements.
    """
    
    waypoint_turn_mode: WaypointTurnMode = Field(
        serialization_alias="waypointTurnMode",
        description="Turn mode for the waypoint"
    )
    
    waypoint_turn_damping_dist: Optional[float] = Field(
        default=None,
        serialization_alias="waypointTurnDampingDist",
        description="Turn damping distance in meters. Defines how far to the waypoint that the aircraft should turn.",
        gt=0
    )
    
    @field_validator('waypoint_turn_mode')
    @classmethod
    def validate_turn_mode(cls, v: Union[WaypointTurnMode, str]) -> WaypointTurnMode:
        """Validate and convert turn mode."""
        if isinstance(v, str):
            try:
                return WaypointTurnMode(v)
            except ValueError:
                raise ValueError(f"Invalid waypoint turn mode: {v}")
        return v
    
    @model_validator(mode='after')
    def validate_mode_requirements(self) -> 'WaypointTurnParam':
        """Validate that required fields are present for specific modes."""
        
        # These modes require waypointTurnDampingDist
        modes_requiring_damping = {
            WaypointTurnMode.COORDINATED_TURN,
            # WaypointTurnMode.CURVED_TURN_WITHOUT_STOP  # from the dji pilot2, this mode does not require damping distance
        }
        
        if (self.waypoint_turn_mode in modes_requiring_damping and 
            self.waypoint_turn_damping_dist is None):
            raise ValueError(
                f"waypointTurnDampingDist is required when waypointTurnMode is '{self.waypoint_turn_mode.value}'"
            )
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with XML-compatible format."""
        result = {
            f"wpml:waypointTurnMode": self.waypoint_turn_mode.value
        }
        
        if self.waypoint_turn_damping_dist is not None:
            result[f"wpml:waypointTurnDampingDist"] = self.waypoint_turn_damping_dist
        
        return result
    
    def to_xml(self) -> str:
        """Convert to XML string."""
        xml_dict = self.to_dict()
        return xmltodict.unparse(xml_dict, pretty=True, full_document=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WaypointTurnParam":
        """Create from dictionary with XML data."""
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
            
            # Convert values to appropriate types
            if field_name == 'waypoint_turn_damping_dist' and value is not None:
                clean_data[field_name] = float(value)
            else:
                clean_data[field_name] = value
        
        return cls(**clean_data)
    
    @classmethod
    def from_xml(cls, xml_data: str) -> "WaypointTurnParam":
        """Create from XML data."""
        try:
            data = xmltodict.parse(xml_data)
            param_data = data.get("wpml:waypointTurnParam", data)
        except:
            raise ValueError("Invalid XML format for waypoint turn parameter")
        
        return cls.from_dict(param_data)
    
    @classmethod
    def create_coordinated_turn(cls, damping_dist: float) -> "WaypointTurnParam":
        """Create turn param for coordinate turn mode."""
        return cls(
            waypoint_turn_mode=WaypointTurnMode.COORDINATED_TURN,
            waypoint_turn_damping_dist=damping_dist
        )
    
    @classmethod
    def create_turn_at_point(cls) -> "WaypointTurnParam":
        """Create turn param for stop with discontinuity curvature mode."""
        return cls(
            waypoint_turn_mode=WaypointTurnMode.TURN_AT_POINT
        )
    
    @classmethod
    def create_curved_turn_with_stop(cls) -> "WaypointTurnParam":
        """Create turn param for stop with continuity curvature mode."""
        return cls(
            waypoint_turn_mode=WaypointTurnMode.CURVED_TURN_WITH_STOP
        )
    
    @classmethod
    def create_curved_turn_without_stop(cls) -> "WaypointTurnParam":
        """Create turn param for pass with continuity curvature mode."""
        return cls(
            waypoint_turn_mode=WaypointTurnMode.CURVED_TURN_WITHOUT_STOP,
        )
    
    def __str__(self) -> str:
        """String representation of turn parameter."""
        result = f"TurnParam(mode={self.waypoint_turn_mode.value}"
        
        if self.waypoint_turn_damping_dist is not None:
            result += f", damping_dist={self.waypoint_turn_damping_dist}m"
        
        result += ")"
        return result