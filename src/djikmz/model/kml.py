from pydantic import BaseModel, Field   
from .mission_config import MissionConfig
from .coordinate_system_param import CoordinateSystemParam
from datetime import datetime
from .heading_param import WaypointHeadingParam 
from .turn_param import WaypointTurnMode
from .waypoint import Waypoint
from enum import Enum
import xmltodict

ATTR_NOT_IN_FOLDER = [
    "wpml:author",
    "wpml:createTime",
    "wpml:updateTime",
    "wpml:missionConfig",
]

class StrEnum(str, Enum):
    """Base class for string enums."""
    def __str__(self):
        return self.value


class GimbalPitchMode(StrEnum):
    """Enumeration of gimbal pitch modes."""
    MANUAL = "manual"
    POINT_SETTING = "usePointSetting"


class KML(BaseModel):
    author: str = Field(
        default="Zey",
        description="Author of the KML file."
    )
    create_time: int = Field(
        default=int(datetime.now().timestamp()*1e3),
        serialization_alias="createTime",
        description="Creation time of the KML file in milliseconds since epoch."
    )
    update_time: int = Field(
        default=int(datetime.now().timestamp()*1e3),
        serialization_alias="updateTime",
        description="Last update time of the KML file in milliseconds since epoch."
    )
    mission_config: MissionConfig = Field(
        default_factory=MissionConfig,
        serialization_alias="missionConfig",
        description="Mission configuration parameters."
    )
    # Those field should under Folder in xml, but we put them here for simplicity since they are also configs.
    template_type: str = Field(
        default="waypoint",
        serialization_alias="templateType",
        description="Type of the KML template, must be 'waypoint' for now",
        pattern="^waypoint$"
    )
    template_id: int = Field(
        default=0,
        serialization_alias="templateId",
        description="ID of the KML template, must be 0 for now",
        ge=0, le=0
    )
    coordinate_system_param: CoordinateSystemParam = Field(
        default_factory=CoordinateSystemParam,
        serialization_alias="waylineCoordinateSysParam",
        description="Coordinate system parameters for the waypoints."
    )
    global_speed: float = Field(
        default=1.0,
        serialization_alias="autoFlightSpeed",
        description="Global flight speed in m/s.",
        ge=0.0)
    global_height: float = Field(
        default=0.0,
        serialization_alias="globalHeight",
        description="Global height of the waypoints in meters.",
        ge=0.0
    )
    global_waypoint_heading_param: WaypointHeadingParam = Field(
        default_factory=WaypointHeadingParam,
        serialization_alias="globalWaypointHeadingParam",
        description="Global heading parameter configuration for the waypoints."
    )
    global_turn_mode: WaypointTurnMode = Field(
        default=WaypointTurnMode.TURN_AT_POINT,
        serialization_alias="globalWaypointTurnMode",
        description="Global turn mode for the waypoints."
    )
    global_use_straight_line: int = Field(
        default=1,
        serialization_alias="globalUseStraightLine",
        description="Use straight line for the waypoints (0: No, 1: Yes)",
        ge=0, le=1
    )
    global_gimbal_pitch_mode: GimbalPitchMode = Field(
        default=GimbalPitchMode.MANUAL,
        serialization_alias="globalGimbalPitchMode",
        description="Global gimbal pitch mode for the waypoints."
    )
    waypoints: list[Waypoint] = Field(
        default_factory=list,
        serialization_alias="Placemark",
        description="List of waypoints in the KML file."
    )

    def to_dict(self) -> dict:
        """Convert the KML to a dictionary."""
        data = self.model_dump(by_alias=True, exclude_none=True, exclude=['waypoints'])
        data = {f"wpml:{k}": v for k, v in data.items()}
        data['Placemark'] = [wp.to_dict() for wp in self.waypoints]
        # expand list and items that have to_dict
        for key, value in data.items():
            if isinstance(value, list):
                data[key] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in value]
            elif hasattr(value, 'to_dict'):
                data[key] = value.to_dict()
        # move attributes that are not in folder to the root
        root_data = {k: v for k, v in data.items() if k  in ATTR_NOT_IN_FOLDER}
        folder_data = {k: v for k, v in data.items() if k not in ATTR_NOT_IN_FOLDER}
        # Add folder data under 'Folder' key
        data = {**root_data, "Folder": folder_data,}
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'KML':
        """Create a KML instance from a dictionary."""
        alias_to_field = {}
        for field_name, field_info in cls.model_fields.items():
            alias = field_info.serialization_alias or field_name
            alias_to_field[alias] = field_name
        folder_data = data.pop("Folder", {})
        data = {**data, **folder_data}
        # Remove wpml: prefix from keys
        clean_data = {k.replace("wpml:", ""): v for k, v in data.items()}
        # Extract waypoints and convert them to Waypoint instances
        waypoints_data = clean_data.pop("Placemark", [])
        waypoints = [Waypoint.from_dict(wp) for wp in waypoints_data]
        # Create the KML instance
        # Generate alias to field mapping automatically
        clean_data = {alias_to_field.get(k, k): v for k, v in clean_data.items()}
        # if a field class have from_dict method, call it 
        for field_name, field_value in clean_data.items():
            field_class = cls.model_fields[field_name].annotation
            if hasattr(field_class, 'from_dict'):
                clean_data[field_name] = field_class.from_dict(field_value) if isinstance(field_value, dict) else field_value
        
        print(clean_data)
        return cls(**clean_data, waypoints=waypoints)
    
    def to_xml(self) -> str:
        """Convert the KML to an XML string."""
        xml_dict = self.to_dict()
        xml_dict = {
            'kml': {
                "@xmlns": "http://www.opengis.net/kml/2.2",
                "@xmlns:wpml": "http://www.dji.com/wpmz/1.0.3",
                "Document": xml_dict
            }
        }
        return xmltodict.unparse(xml_dict, pretty=True)
    
    @classmethod
    def from_xml(cls, xml_data: str) -> 'KML':
        """Create a KML instance from an XML string."""
        data = xmltodict.parse(xml_data, force_list=('Placemark',))
        data = data.get('kml', {}).get('Document', {})
        # Handle both cases: with and without root element
        return cls.from_dict(data)
    