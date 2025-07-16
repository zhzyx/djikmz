import xmltodict
from .action import Action
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, Any, List, Optional, Union
from enum import Enum

class TriggerType(str, Enum):
    def __str__(self):
        return self.value
    REACH_POINT = "reachPoint"
    BETWEEN_POINTS = "betweenAdjacentPoints"
    MULTIPLE_TIMING = "multipleTiming"
    MULTIPLE_DISTANCE = "multipleDistance"

class ActionTrigger(BaseModel):
    type: TriggerType|str = Field(
        default=TriggerType.REACH_POINT,
        serialization_alias="actionTriggerType",
        description="Type of action trigger"
    )
    @field_validator('type')
    def validate_trigger_type(cls, value: Union[TriggerType, str]) -> TriggerType:
        if isinstance(value, str):
            value = TriggerType(value)
        if not isinstance(value, TriggerType):
            raise ValueError(f"actionTriggerType must be a TriggerType or valid string, got {type(value)}")
        return value
    param: float|None = Field(
        default=None,
        serialization_alias="actionTriggerParam",
        description="Parameter for the action trigger multiple timing and multiple distance; " \
                    "time in second or distance in meter respectively"
    )
    def to_dict(self) -> Dict[str, Any]:
        """Convert the ActionTrigger to a dictionary."""
        d = self.model_dump(by_alias=True, exclude_none=True)
        return {f"wpml:{key}": value for key, value in d.items() if value is not None}

    def to_xml(self) -> str:
        """Convert the ActionTrigger to an XML string."""
        xml_dict = self.to_dict()
        return xmltodict.unparse(xml_dict, pretty=True, full_document=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any] = None):
        """Create ActionTrigger from a dictionary."""
        if data is None:
            data = {}
        trigger_type = TriggerType(data.get("wpml:actionTriggerType", TriggerType.REACH_POINT))
        param = data.get("wpml:actionTriggerParam", None)
        return cls(type=trigger_type, param=param)
    
    @classmethod
    def from_xml(cls, xml_data: str):
        """Create ActionTrigger from XML data."""
        data = xmltodict.parse(xml_data)["wpml:actionTrigger"]
        trigger_type_str = data.get("wpml:actionTriggerType")
        if trigger_type_str is None:
            trigger_type = TriggerType.REACH_POINT
        else:
            trigger_type = TriggerType(trigger_type_str)
        param = data.get("wpml:actionTriggerParam", None)
        if param is not None:
            param = float(param)  
        return cls(type=trigger_type, param=param)

class ActionGroup(BaseModel):
    """
    Represents a group of actions to be executed together.
    This is used to encapsulate multiple actions in a single command.
    """

    group_id: int = Field(
        default=0,
        serialization_alias="actionGroupId",
        description="Unique identifier for the action group",
        ge=0
    )
    start_waypoint_id: int = Field(
        default=None,
        serialization_alias="actionGroupStartIndex",
        description="ID of the waypoint where this action group starts"
    )
    end_waypoint_id: int = Field(
        default=None,
        serialization_alias="actionGroupEndIndex",
        description="ID of the waypoint where this action group ends"
    )
    execution_mode: str = Field(
        default="sequence",
        serialization_alias="actionGroupMode",
        description="only sequence"
    )
    actions: List[Action] = Field(
        default_factory=list,
        serialization_alias="action",
        description="Dictionary of actions in this group"
    )
    trigger: ActionTrigger = Field(
        default_factory=ActionTrigger,
        serialization_alias="actionTrigger",
        description="Trigger for the action group"
    )
    @model_validator(mode="after")
    def validate_start_end(self) -> "ActionGroup":
        """Ensure start and end waypoint IDs are set correctly."""
        if self.start_waypoint_id is None:
            self.start_waypoint_id = self.group_id  # Default to group_id if not set
        if self.end_waypoint_id is None:
            self.end_waypoint_id = self.start_waypoint_id  # Default to start if not set
        if self.start_waypoint_id < self.group_id:
            raise ValueError("start_waypoint_id must be greater than or equal to group_id")
        if self.end_waypoint_id < self.start_waypoint_id:
            raise ValueError("end_waypoint_id must be greater than or equal to start_waypoint_id")
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ActionGroup to a dictionary."""
        # the action and trigger fields need to use their own to_dict
        actions_dict = [action.to_dict() for action in self.actions]
        trigger_dict = self.trigger.to_dict() if self.trigger else {}
        data = self.model_dump(by_alias=True, exclude_none=True, exclude={"actions", "trigger"})
        data = {f"wpml:{key}": value for key, value in data.items() if value is not None}
        data["wpml:action"] = actions_dict
        data["wpml:actionTrigger"] = trigger_dict
        return data
    
    def to_xml(self) -> str:
        """Convert the ActionGroup to an XML string."""
        xml_dict = self.to_dict()
        return xmltodict.unparse({"wpml:actionGroup": xml_dict}, pretty=True, full_document=False)

    @classmethod
    def from_xml(cls, xml_data: str):
        """Create ActionGroup from XML data."""
        data = xmltodict.parse(xml_data)["wpml:actionGroup"]
        group_id = int(data.get("wpml:actionGroupId", 0))
        start_waypoint_id = int(data.get("wpml:actionGroupStartIndex", 0))
        end_waypoint_id = int(data.get("wpml:actionGroupEndIndex", 0))
        execution_mode = data.get("wpml:actionGroupMode", "sequence")
        actions = data.get("wpml:action", [])
        actions = [Action.from_dict(action) for action in actions]
        trigger = ActionTrigger.from_dict(data.get("wpml:actionTrigger", None))
        return cls(
            group_id=group_id,
            start_waypoint_id=start_waypoint_id,
            end_waypoint_id=end_waypoint_id,
            execution_mode=execution_mode,
            actions=actions,
            trigger=trigger
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionGroup":
        """Create ActionGroup from a dictionary."""
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
            
            # Handle special cases for complex types
            if field_name == 'actions' and value:
                if isinstance(value, list):
                    clean_data[field_name] = [Action.from_dict(action) for action in value]
                else:
                    clean_data[field_name] = [Action.from_dict(value)]
            elif field_name == 'trigger' and value:
                clean_data[field_name] = ActionTrigger.from_dict(value)
            else:
                clean_data[field_name] = value
        
        return cls(**clean_data)
    
    def _renumber_actions(self):
        """Renumber all actions to have sequential IDs starting from 1."""
        for i, action in enumerate(self.actions, 1):
            # Create a new action with updated ID to maintain immutability
            action_dict = action.model_dump()
            action_dict['action_id'] = i
            # Replace the action with a new instance with updated ID
            self.actions[i-1] = type(action)(**action_dict)
    
    def add_action(self, action: Action, auto_id: bool = True) -> None:
        """
        Add an action to the group.
        
        Args:
            action: The action to add
            auto_id: If True, automatically assign the next sequential ID
        """
        if auto_id:
            new_id = len(self.actions) + 1
            action_dict = action.model_dump()
            action_dict['action_id'] = new_id
            action = type(action)(**action_dict)
        
        self.actions.append(action)
    
    def insert_action(self, index: int, action: Action, auto_renumber: bool = True) -> None:
        """
        Insert an action at a specific position.
        
        Args:
            index: Position to insert at (0-based)
            action: The action to insert
            auto_renumber: If True, renumber all actions after insertion
        """
        if index < 0 or index > len(self.actions):
            raise ValueError(f"Index {index} out of range for {len(self.actions)} actions")
        
        self.actions.insert(index, action)
        
        if auto_renumber:
            self._renumber_actions()
    
    def remove_action(self, action_id: int, auto_renumber: bool = True) -> bool:
        """
        Remove an action by its ID.
        
        Args:
            action_id: ID of the action to remove
            auto_renumber: If True, renumber remaining actions
            
        Returns:
            True if action was found and removed, False otherwise
        """
        for i, action in enumerate(self.actions):
            if action.action_id == action_id:
                self.actions.pop(i)
                if auto_renumber:
                    self._renumber_actions()
                return True
        return False
    
    def remove_action_at(self, index: int, auto_renumber: bool = True) -> Action:
        """
        Remove an action at a specific position.
        
        Args:
            index: Position to remove from (0-based)
            auto_renumber: If True, renumber remaining actions
            
        Returns:
            The removed action
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.actions):
            raise IndexError(f"Index {index} out of range for {len(self.actions)} actions")
        
        removed_action = self.actions.pop(index)
        
        if auto_renumber:
            self._renumber_actions()
            
        return removed_action
    
    def move_action(self, from_index: int, to_index: int, auto_renumber: bool = True) -> None:
        """
        Move an action from one position to another.
        
        Args:
            from_index: Current position of the action (0-based)
            to_index: New position for the action (0-based)
            auto_renumber: If True, renumber all actions after move
        """
        if from_index < 0 or from_index >= len(self.actions):
            raise IndexError(f"From index {from_index} out of range")
        if to_index < 0 or to_index >= len(self.actions):
            raise IndexError(f"To index {to_index} out of range")
        
        action = self.actions.pop(from_index)
        self.actions.insert(to_index, action)
        
        if auto_renumber:
            self._renumber_actions()
    
    def clear_actions(self) -> None:
        """Remove all actions from the group."""
        self.actions.clear()
    
    def get_action_by_id(self, action_id: int) -> Optional[Action]:
        """
        Get an action by its ID.
        
        Args:
            action_id: ID of the action to find
            
        Returns:
            The action if found, None otherwise
        """
        for action in self.actions:
            if action.action_id == action_id:
                return action
        return None
    
    
    @property
    def action_count(self) -> int:
        """Get the number of actions in this group."""
        return len(self.actions)
    
    @property
    def next_action_id(self) -> int:
        """Get the next available action ID."""
        return len(self.actions) + 1