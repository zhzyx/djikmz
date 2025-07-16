from pydantic import BaseModel, Field, computed_field, model_serializer
from typing import Optional, Dict, Any, Union
from enum import Enum
import xmltodict

class FlyToWaylineMode(str, Enum):
    SAFELY = "safely"
    POINTTOPOINT = "pointToPoint"

    def __str__(self):
        return self.value


class FinishAction(str, Enum):
    GO_HOME = "goHome"
    AUTOLAND = "autoLand"
    GOTO_FIRST_WAYPOINT = "gotoFirstWaypoint"
    NO_ACTION = "noAction"

    def __str__(self):
        return self.value

class RCLostAction(str, Enum):
    """
    DJI kmz first use exitOnRCLost to specify whether `goContinue` or other actions(`executeLostAction`). 
    if use other actions, one have to specify the action in `executeRCLostAction`. using  `hover` `goBack` `landing` etc
    """
    CONTINUE = "goContinue"
    HOVER = "handover"
    GO_HOME = "goBack"
    LAND = "landing"

    def __str__(self):
        return self.value
    
class DroneModel(str, Enum):
    M350 = "M350"
    M300 = "M300"
    M30 = "M30"
    M30T = "M30T"
    M3E = "M3E"
    M3T = "M3T"
    M3M = "M3M"
    M3D = "M3D"
    M3TD = "M3TD"
    def __str__(self):
        return self.value

MODEL_TO_VAL = {
    DroneModel.M350: [89, None],
    DroneModel.M300: [60, None],
    DroneModel.M30: [67, 0],
    DroneModel.M30T: [67, 1],
    DroneModel.M3E: [77, 0],
    DroneModel.M3T: [77, 1],
    DroneModel.M3M: [77, 2],
    DroneModel.M3D: [91, 0],
    DroneModel.M3TD: [91, 1],
}

class PayloadModel(int, Enum):
    H20 = 42
    H20T = 43
    P1 = 50
    M30 = 52
    M30T = 53
    H20N = 61
    M3E = 66
    M3T = 67
    M3M = 68
    M3D = 80
    M3TD = 81
    H30 = 82
    H30T = 83
    PSDK = 65534

    def __str__(self):
        return str(self.value)

class DroneInfo(BaseModel):
    drone_model: DroneModel = Field(
        default=DroneModel.M350)
    @computed_field(alias='droneEnumValue')
    @property
    def drone_enum_value(self) -> int:
        """
        Returns the enum value for the drone model.
        """
        return MODEL_TO_VAL[self.drone_model][0]
    @computed_field(alias='droneSubEnumValue')
    @property
    def drone_sub_enum_value(self) -> Optional[int]:
        """
        Returns the sub enum value for the drone model.
        """
        return MODEL_TO_VAL[self.drone_model][1]
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the DroneInfo to a dictionary.
        """
        data = self.model_dump(by_alias=True, exclude_none=True, exclude=["drone_model"])
        data = {f"wpml:{k}": v for k, v in data.items()}
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DroneInfo':
        """
        Create a DroneInfo instance from a dictionary.
        """
        # Handle both prefixed and non-prefixed keys
        drone_enum_value = data.get('wpml:droneEnumValue') or data.get('droneEnumValue')
        drone_sub_enum_value = data.get('wpml:droneSubEnumValue') or data.get('droneSubEnumValue')
        
        if drone_enum_value is None:
            raise ValueError("droneEnumValue is required")
        
        # Convert to int if it's a string
        drone_enum_value = int(drone_enum_value)
        if drone_sub_enum_value is not None:
            drone_sub_enum_value = int(drone_sub_enum_value)
        
        # iterate through MODEL_TO_VAL to find the matching drone model
        for model, (enum_value, sub_enum_value) in MODEL_TO_VAL.items():
            if enum_value == drone_enum_value and (sub_enum_value is None or sub_enum_value == drone_sub_enum_value):
                return cls(drone_model=model)
        raise ValueError(f"Unknown drone model with enum value {drone_enum_value} and sub enum value {drone_sub_enum_value}")
    
    def to_xml(self) -> str:
        """
        Convert the DroneInfo to XML format.
        """
        return xmltodict.unparse(self.to_dict(), pretty=True, full_document=False)
    
    @classmethod
    def from_xml(cls, xml_data: str) -> 'DroneInfo':
        """
        Create a DroneInfo instance from XML data.
        """
        data = xmltodict.parse(xml_data)
        drone_data = data.get('wpml:droneInfo', data)
        if drone_data is None:
            raise ValueError("Invalid XML data: 'droneInfo' not found.")
        # Remove the wpml: prefix from keys
        drone_data = {k.replace("wpml:", ""): v for k, v in drone_data.items()}
        return cls.from_dict(drone_data)
    

class PayloadInfo(BaseModel):
    payload_model: PayloadModel = Field(
        default=PayloadModel.M3M,
        serialization_alias="payloadEnumValue",
        description="Payload model for the mission. This is used to determine the capabilities of the payload.")
    position: int = Field(
        default=0,
        serialization_alias="payloadPositionIndex",
        description="Position of the payload on the drone. 0 is default position, 1 is the front right for dual mount, 2 is the top")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the PayloadInfo to a dictionary.
        """
        data = {field.serialization_alias or name: getattr(self,name) for name , field in type(self).model_fields.items() if getattr(self, name) is not None}
        data = {f"wpml:{k}": v for k, v in data.items()}
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PayloadInfo':
        # Handle both prefixed and non-prefixed keys
        clean_data = {k.replace("wpml:", ""): v for k, v in data.items()}
        params = {}
        
        for field_name, field_info in cls.model_fields.items():
            alias = field_info.serialization_alias or field_name
            if alias in clean_data:
                value = clean_data[alias]
                # Convert payload enum value to PayloadModel
                if field_name == 'payload_model':
                    try:
                        params[field_name] = PayloadModel(int(value))
                    except (ValueError, TypeError):
                        params[field_name] = PayloadModel.M3M  # Default fallback
                else:
                    params[field_name] = value
        
        return cls(**params)
    
    def to_xml(self) -> str:
        """Convert the PayloadInfo to XML format."""
        xml_dict = self.to_dict()
        return xmltodict.unparse(xml_dict, pretty=True, full_document=False)
    
    @classmethod
    def from_xml(cls, xml_data: str) -> 'PayloadInfo':
        """Create a PayloadInfo instance from XML data."""
        try:
            data = xmltodict.parse(xml_data)
            payload_data = data.get("wpml:payloadInfo", data)
        except:
            raise ValueError("Invalid XML format for payload info")
        
        return cls.from_dict(payload_data)
    
    @model_serializer
    def serialize(self) -> Dict[str, Any]:
        """Serialize the PayloadInfo to a dictionary."""
        return self.to_dict()
    

class MissionConfig(BaseModel):
    """
    Mission configuration for DJI task
    """
    fly_to_wayline_mode: FlyToWaylineMode = Field(
        default=FlyToWaylineMode.SAFELY,
        serialization_alias="flyToWaylineMode",
        description="Mode for flying to wayline")
    finish_action: FinishAction = Field(
        default=FinishAction.GO_HOME,
        serialization_alias="finishAction",
        description="Action to take when mission finishes")
    rclost_action: RCLostAction = Field(
        default=RCLostAction.CONTINUE,
        description="Action to take when RC connection is lost")
    @computed_field(alias='exitOnRCLost')
    @property
    def exit_on_rc_lost(self) -> str:
        if self.rclost_action == RCLostAction.CONTINUE:
            return "goContinue"
        else:
            return "executeLostAction"
    @computed_field(alias='executeRCLostAction')
    @property
    def execute_rc_lost_action(self) -> Optional[str]:
        if self.rclost_action == RCLostAction.CONTINUE:
            return None
        else:
            return str(self.rclost_action)
    take_off_height: float = Field(
        default=1.2,
        serialization_alias="takeOffSecurityHeight",
        description="Take off security height in meters. This is the height that the aircraft will fly to before starting the mission." \
                    " It is used to avoid obstacles during takeoff.",
        ge=1.2, le=1500.0)
    ref_take_off: None = Field(
        default=None,
        serialization_alias="refTakeOffPoint",
        description="Reference Takeoff Point is only for reference of route planning. nothing to do with actual mission. Not implemented yet.")
    ref_take_off_altitude: None = Field(
        default=None,
        serialization_alias="takeOffRefPointAGLHeight",
        description=" The altitude of `reference take-off point` corresponds to the ellipsoid height in reference take-off point. Not implemented yet.")
    drone_info: Optional[DroneInfo] = Field(
        default=None,
        serialization_alias="droneInfo",
        description="Drone information for the mission. "
    )
    payload_info: Optional[PayloadInfo] = Field(
        default=None,
        serialization_alias="payloadInfo",
        description="Payload information for the mission. "
    )
    def to_dict(self) -> Dict[str, Any]:
        """Convert the MissionConfig to a dictionary."""
        data = {field.serialization_alias or name: getattr(self,name) for name , field in type(self).model_fields.items() if getattr(self, name) is not None}
        data['exitOnRCLost'] = self.exit_on_rc_lost # Add computed field
        if self.execute_rc_lost_action is not None:
            data['executeRCLostAction'] = self.execute_rc_lost_action  # Add computed field
        data.pop("rclost_action", None)  # Remove computed field from serialization
        for k, v in data.items():
            if isinstance(v, Enum):
                data[k] = str(v)
            elif isinstance(v, BaseModel):
                data[k] = v.model_dump()
        data = {f"wpml:{k}": v for k, v in data.items()}
        
        # Handle complex nested objects
        if self.drone_info:
            data["wpml:droneInfo"] = self.drone_info.to_dict()
        if self.payload_info:
            data["wpml:payloadInfo"] = self.payload_info.to_dict()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MissionConfig':
        """Create a MissionConfig instance from a dictionary."""
        # Generate alias to field mapping automatically
        alias_to_field = {}
        for field_name, field_info in cls.model_fields.items():
            alias = field_info.serialization_alias or field_name
            alias_to_field[alias] = field_name
        
        clean_data = {}
        
        # Handle RC lost action mapping from computed fields
        exit_on_rc_lost = data.get("wpml:exitOnRCLost")
        execute_rc_lost_action = data.get("wpml:executeRCLostAction")
        
        if exit_on_rc_lost is not None:
            if exit_on_rc_lost == "goContinue":
                clean_data["rclost_action"] = RCLostAction.CONTINUE
            elif exit_on_rc_lost == "executeLostAction" and execute_rc_lost_action:
                # Map the executeRCLostAction value back to RCLostAction enum
                if execute_rc_lost_action == "handover":
                    clean_data["rclost_action"] = RCLostAction.HOVER
                elif execute_rc_lost_action == "goBack":
                    clean_data["rclost_action"] = RCLostAction.GO_HOME
                elif execute_rc_lost_action == "landing":
                    clean_data["rclost_action"] = RCLostAction.LAND
                else:
                    clean_data["rclost_action"] = RCLostAction.CONTINUE  # Default fallback
        
        # Process each field, removing wpml: prefix and mapping aliases
        for key, value in data.items():
            clean_key = key.replace("wpml:", "")
            
            # Skip computed fields as they're handled above
            if clean_key in ["exitOnRCLost", "executeRCLostAction"]:
                continue
            
            # Map alias to actual field name
            field_name = alias_to_field.get(clean_key, clean_key)
            
            # Handle special cases for complex types
            if field_name == 'drone_info' and value:
                clean_data[field_name] = DroneInfo.from_dict(value)
            elif field_name == 'payload_info' and value:
                clean_data[field_name] = PayloadInfo.from_dict(value)
            else:
                clean_data[field_name] = value
        
        return cls(**clean_data)
    
    def to_xml(self) -> str:
        """Convert the MissionConfig to XML format."""
        xml_dict = self.to_dict()
        return xmltodict.unparse(xml_dict, pretty=True, full_document=False)
    
    @classmethod
    def from_xml(cls, xml_data: str) -> 'MissionConfig':
        """Create a MissionConfig instance from XML data."""
        try:
            data = xmltodict.parse(xml_data)
            config_data = data.get("wpml:missionConfig", data)
        except:
            raise ValueError("Invalid XML format for mission config")
        
        return cls.from_dict(config_data)
    
    @model_serializer
    def serialize(self) -> Dict[str, Any]:
        """Serialize the MissionConfig to a dictionary."""
        return self.to_dict()



