from typing import Dict, Any, Optional, Union
from enum import Enum
# from dataclasses import dataclass, fields, is_dataclass, field
from pydantic import BaseModel, Field, field_validator, model_serializer
import xmltodict

from .registry import ACTION_REGISTRY


class ActionType(str, Enum):
    """Valid DJI action types."""
    TAKE_PHOTO = "takePhoto"
    START_RECORD = "startRecord"
    STOP_RECORD = "stopRecord"
    GIMBAL_ROTATE = "gimbalRotate"
    HOVER = "hover"
    ROTATE_YAW = "rotateYaw"
    FOCUS = "focus"
    ZOOM = "zoom"
    ACCURATE_SHOOT = "accurateShoot"  # Dji doc says this is legacy, use orientedShoot instead
    ORIENTED_SHOOT = "orientedShoot"
    PANO_SHOT = "panoShot"
    RECORD_POINT_CLOUD = "recordPointCloud"
    GIMBAL_EVENLY_ROTATE = "gimbalEvenlyRotate"

    def __str__(self):
        """Return the string representation of the action type."""
        return self.value

class Action(BaseModel):
    """
    Action specific parameters stored in action_actuator_func_param(actionActuatorFuncParam).
    """

    action_id: int = Field(default=0, serialization_alias="actionId", ge=0, le=65535)
    action_type: ActionType = Field(
        default=None, 
        serialization_alias="actionActuatorFunc",
        frozen=True  # Make this field immutable after initialization
    )

    @field_validator('action_type')
    def validate_action_type(cls, value: Union[ActionType, str]) -> ActionType:
        if isinstance(value, str):
            value = ActionType(value)
        if not isinstance(value, ActionType):
            raise ValueError(f"action_type must be an ActionType or valid string, got {type(value)}")
        return value
    
    def model_post_init(self, __context) -> None:
        if self.action_type is None:
            for action_type, registered_class in ACTION_REGISTRY.items():
                if registered_class == self.__class__:
                    # Use object.__setattr__ to bypass frozen restriction
                    object.__setattr__(self, 'action_type', action_type)
                    break
            else:
                raise ValueError(f"Action class {self.__class__.__name__} not found in ACTION_REGISTRY")

    def to_dict(self) -> Dict[str, Any]:
        data = {field.serialization_alias or name: getattr(self,name) for name , field in type(self).model_fields.items() if getattr(self, name) is not None}
        header_keys = {
            field.serialization_alias or name for name, field in Action.model_fields.items()
        } 

        header = {
            f"wpml:{key}": data[key] for key in header_keys if key in data
        }
        action_params = {
            f"wpml:{key}": value for key, value in data.items() if key not in header_keys
        }
        return { **header, "wpml:actionActuatorFuncParam": action_params }
    
    def to_xml(self) -> str:
        """Convert the action to an XML string."""
        xml_dict = self.to_dict()
        return xmltodict.unparse(xml_dict, pretty=True, full_document=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create Action from a dictionary."""
        action_id = int(data.get("wpml:actionId", 0))
        action_type = ActionType(data.get("wpml:actionActuatorFunc", None))
        action_cls = ACTION_REGISTRY.get(action_type, cls)
        
        # Only use fields defined directly in the action_cls, not inherited from Action
        parent_fields = set(Action.model_fields.keys())
        cls_fields = {name: field for name, field in action_cls.model_fields.items() if name not in parent_fields}
        
        # Only include non-None parameters to let Pydantic use default values
        cls_params = {}
        cls_params_data = data.get("wpml:actionActuatorFuncParam", {})
        cls_params_data = {k.replace("wpml:", ""): v for k, v in cls_params_data.items()}
        for name, field in cls_fields.items():
            alias = field.serialization_alias or name
            if alias in cls_params_data and cls_params_data[alias] is not None:
                cls_params[name] = cls_params_data[alias]
        return action_cls(action_id=action_id, **cls_params)
    
    @classmethod
    def from_xml(cls, xml_data: str):
        """Create Action from XML data."""
        data = xmltodict.parse(xml_data)["wpml:action"]
        action_id = int(data["wpml:actionId"])
        action_type = ActionType(data.get("wpml:actionActuatorFunc")) 
        action_cls = ACTION_REGISTRY[action_type]
        action_params = data.get("wpml:actionActuatorFuncParam", {})
        
        # Handle case where actionActuatorFuncParam is None (empty element)
        if action_params is None:
            action_params = {}
        
        # Only use fields defined directly in the action_cls, not inherited from Action
        parent_fields = set(Action.model_fields.keys())
        cls_fields = {name: field for name, field in action_cls.model_fields.items() if name not in parent_fields}
        
        # Only include non-None parameters to let Pydantic use default values
        cls_params = {}
        for name, field in cls_fields.items():
            xml_key = f"wpml:{field.serialization_alias}"
            if xml_key in action_params and action_params[xml_key] is not None:
                cls_params[name] = action_params[xml_key]
        
        return action_cls(action_id=action_id, **cls_params)
    
    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return self.to_dict()



