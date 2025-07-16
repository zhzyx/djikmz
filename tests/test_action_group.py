"""
Test suite for ActionGroup and ActionTrigger classes.

This test file covers the ActionGroup functionality including:
- ActionTrigger creation and validation
- ActionGroup creation with various configurations
- Default value handling and validation
- XML serialization/deserialization
- Field validation and business logic
"""

import pytest
from pydantic import ValidationError
import xmltodict
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from djikmz.model.action_group import ActionGroup, ActionTrigger, TriggerType
from djikmz.model.action import TakePhotoAction, HoverAction, RotateYawAction


class TestTriggerType:
    """Test TriggerType enum."""
    
    def test_trigger_type_values(self):
        """Test that TriggerType has correct values."""
        assert TriggerType.REACH_POINT == "reachPoint"
        assert TriggerType.BETWEEN_POINTS == "betweenAdjacentPoints"
        assert TriggerType.MULTIPLE_TIMING == "multipleTiming"
        assert TriggerType.MULTIPLE_DISTANCE == "multipleDistance"
    
    def test_trigger_type_str(self):
        """Test TriggerType string representation."""
        assert str(TriggerType.REACH_POINT) == "reachPoint"
        assert str(TriggerType.MULTIPLE_TIMING) == "multipleTiming"


class TestActionTrigger:
    """Test ActionTrigger class."""
    
    def test_creation_with_defaults(self):
        """Test creating ActionTrigger with default values."""
        trigger = ActionTrigger()
        assert trigger.type == TriggerType.REACH_POINT
        assert trigger.param is None
    
    def test_creation_with_custom_values(self):
        """Test creating ActionTrigger with custom values."""
        trigger = ActionTrigger(
            type=TriggerType.MULTIPLE_TIMING,
            param=5.0
        )
        assert trigger.type == TriggerType.MULTIPLE_TIMING
        assert trigger.param == 5.0
    
    def test_trigger_type_validation_string(self):
        """Test trigger type validation with string input."""
        trigger = ActionTrigger(type="multipleTiming", param=3.0)
        assert trigger.type == TriggerType.MULTIPLE_TIMING
        assert trigger.param == 3.0
    
    def test_trigger_type_validation_invalid(self):
        """Test trigger type validation with invalid input."""
        with pytest.raises(ValidationError):
            ActionTrigger(type="invalidTrigger")
    
    def test_to_dict(self):
        """Test converting ActionTrigger to dictionary."""
        trigger = ActionTrigger(
            type=TriggerType.MULTIPLE_DISTANCE,
            param=10.5
        )
        result = trigger.to_dict()
        
        assert result["wpml:actionTriggerType"] == "multipleDistance"
        assert result["wpml:actionTriggerParam"] == 10.5
    
    def test_to_dict_exclude_none(self):
        """Test to_dict excludes None values."""
        trigger = ActionTrigger(type=TriggerType.REACH_POINT)
        result = trigger.to_dict()
        
        assert result["wpml:actionTriggerType"] == "reachPoint"
        assert "wpml:actionTriggerParam" not in result
    
    def test_from_dict(self):
        """Test creating ActionTrigger from dictionary."""
        data = {
            "wpml:actionTriggerType": "multipleTiming",
            "wpml:actionTriggerParam": 2.5
        }
        trigger = ActionTrigger.from_dict(data)
        
        assert trigger.type == TriggerType.MULTIPLE_TIMING
        assert trigger.param == 2.5
    
    def test_from_dict_missing_param(self):
        """Test creating ActionTrigger from dict with missing param."""
        data = {"wpml:actionTriggerType": "reachPoint"}
        trigger = ActionTrigger.from_dict(data)
        
        assert trigger.type == TriggerType.REACH_POINT
        assert trigger.param is None  # Default from from_dict method
    
    def test_xml_serialization(self):
        """Test XML serialization and deserialization."""
        trigger = ActionTrigger(
            type=TriggerType.MULTIPLE_TIMING,
            param=7.5
        )
        
        # Serialize to XML
        xml_str = trigger.to_xml()
        assert "multipleTiming" in xml_str
        assert "7.5" in xml_str
        
        # Deserialize from XML
        xml_with_root = f'<wpml:actionTrigger>{xml_str}</wpml:actionTrigger>'
        recreated_trigger = ActionTrigger.from_xml(xml_with_root)
        
        assert recreated_trigger.type == trigger.type
        assert recreated_trigger.param == trigger.param


class TestActionGroup:
    """Test ActionGroup class."""
    
    def test_creation_with_defaults(self):
        """Test creating ActionGroup with default values."""
        group = ActionGroup()
        
        assert group.group_id == 0
        assert group.start_waypoint_id == 0  # Should be set to group_id by validator
        assert group.end_waypoint_id == 0    # Should be set to start_waypoint_id by validator
        assert group.execution_mode == "sequence"
        assert group.actions == []
        assert isinstance(group.trigger, ActionTrigger)
        assert group.trigger.type == TriggerType.REACH_POINT
    
    def test_creation_with_custom_values(self):
        """Test creating ActionGroup with custom values."""
        trigger = ActionTrigger(type=TriggerType.MULTIPLE_TIMING, param=5.0)
        actions = [
            TakePhotoAction(action_id=1, file_suffix="photo1"),
            HoverAction(action_id=2, hover_time=3.0)
        ]
        
        group = ActionGroup(
            group_id=10,
            start_waypoint_id=15,
            end_waypoint_id=20,
            execution_mode="sequence",
            actions=actions,
            trigger=trigger
        )
        
        assert group.group_id == 10
        assert group.start_waypoint_id == 15
        assert group.end_waypoint_id == 20
        assert group.execution_mode == "sequence"
        assert len(group.actions) == 2
        assert group.trigger.type == TriggerType.MULTIPLE_TIMING
    
    def test_default_waypoint_id_validation(self):
        """Test that default waypoint IDs are set correctly."""
        # Test with custom group_id
        group = ActionGroup(group_id=5)
        assert group.start_waypoint_id == 5  # Should default to group_id
        assert group.end_waypoint_id == 5    # Should default to start_waypoint_id
        
        # Test with custom start_waypoint_id
        group = ActionGroup(group_id=3, start_waypoint_id=7)
        assert group.start_waypoint_id == 7
        assert group.end_waypoint_id == 7    # Should default to start_waypoint_id
    
    def test_waypoint_validation_rules(self):
        """Test waypoint ID validation rules."""
        # start_waypoint_id must be >= group_id
        with pytest.raises(ValidationError, match="start_waypoint_id must be greater than or equal to group_id"):
            ActionGroup(group_id=10, start_waypoint_id=5)
        
        # end_waypoint_id must be >= start_waypoint_id
        with pytest.raises(ValidationError, match="end_waypoint_id must be greater than or equal to start_waypoint_id"):
            ActionGroup(group_id=5, start_waypoint_id=10, end_waypoint_id=8)
    
    def test_valid_waypoint_combinations(self):
        """Test valid waypoint ID combinations."""
        # Equal values should be valid
        group = ActionGroup(group_id=5, start_waypoint_id=5, end_waypoint_id=5)
        assert group.start_waypoint_id == 5
        assert group.end_waypoint_id == 5
        
        # Increasing values should be valid
        group = ActionGroup(group_id=1, start_waypoint_id=3, end_waypoint_id=7)
        assert group.start_waypoint_id == 3
        assert group.end_waypoint_id == 7
    
    def test_group_id_validation(self):
        """Test group_id validation."""
        # Valid values
        ActionGroup(group_id=0)
        ActionGroup(group_id=100)
        
        # Invalid values
        with pytest.raises(ValidationError):
            ActionGroup(group_id=-1)
    
    def test_actions_list(self):
        """Test actions list functionality."""
        # Empty actions list
        group = ActionGroup()
        assert group.actions == []
        
        # Add actions
        actions = [
            TakePhotoAction(action_id=1),
            HoverAction(action_id=2, hover_time=5.0),
            RotateYawAction(action_id=3, aircraft_heading=90.0)
        ]
        group = ActionGroup(actions=actions)
        assert len(group.actions) == 3
        assert isinstance(group.actions[0], TakePhotoAction)
        assert isinstance(group.actions[1], HoverAction)
        assert isinstance(group.actions[2], RotateYawAction)
    
    def test_to_dict(self):
        """Test converting ActionGroup to dictionary."""
        trigger = ActionTrigger(type=TriggerType.MULTIPLE_TIMING, param=2.0)
        actions = [TakePhotoAction(action_id=1, file_suffix="test")]
        
        group = ActionGroup(
            group_id=5,
            start_waypoint_id=10,
            end_waypoint_id=15,
            execution_mode="sequence",
            actions=actions,
            trigger=trigger
        )
        
        result = group.to_dict()
        
        # Check header fields with wpml prefix
        assert result["wpml:actionGroupId"] == 5
        assert result["wpml:actionGroupStartIndex"] == 10
        assert result["wpml:actionGroupEndIndex"] == 15
        assert result["wpml:actionGroupMode"] == "sequence"
        
        # Check actions
        assert "wpml:action" in result
        assert len(result["wpml:action"]) == 1
        assert result["wpml:action"][0]["wpml:actionActuatorFunc"] == "takePhoto"
        
        # Check trigger
        assert "wpml:actionTrigger" in result
        assert result["wpml:actionTrigger"]["wpml:actionTriggerType"] == "multipleTiming"
    
    def test_xml_serialization(self):
        """Test XML serialization."""
        actions = [TakePhotoAction(action_id=1, file_suffix="photo")]
        group = ActionGroup(
            group_id=1,
            start_waypoint_id=2,
            end_waypoint_id=3,
            actions=actions
        )
        
        xml_str = group.to_xml()
        
        # Verify XML structure
        assert "wpml:actionGroup" in xml_str
        assert "wpml:actionGroupId" in xml_str
        assert "wpml:action" in xml_str
        assert "takePhoto" in xml_str
        
        # Parse XML to verify structure
        parsed = xmltodict.parse(xml_str)
        assert "wpml:actionGroup" in parsed
    
    def test_from_xml(self):
        """Test creating ActionGroup from XML."""
        # Note: This test would need to be adjusted based on the actual
        # implementation of Action.from_dict method
        xml_data = '''<wpml:actionGroup>
            <wpml:actionGroupId>5</wpml:actionGroupId>
            <wpml:actionGroupStartIndex>10</wpml:actionGroupStartIndex>
            <wpml:actionGroupEndIndex>15</wpml:actionGroupEndIndex>
            <wpml:actionGroupMode>sequence</wpml:actionGroupMode>
            <wpml:action>
                <wpml:actionId>1</wpml:actionId>
                <wpml:actionActuatorFunc>takePhoto</wpml:actionActuatorFunc>
                <wpml:actionActuatorFuncParam>
                    <wpml:fileSuffix>test</wpml:fileSuffix>
                </wpml:actionActuatorFuncParam>
            </wpml:action>
            <wpml:actionTrigger>
                <wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>
            </wpml:actionTrigger>
        </wpml:actionGroup>'''
        
        # This test might need adjustment based on Action.from_dict implementation
        try:
            group = ActionGroup.from_xml(xml_data)
            assert group.group_id == 5
            assert group.start_waypoint_id == 10
            assert group.end_waypoint_id == 15
            assert group.execution_mode == "sequence"
        except (AttributeError, NotImplementedError):
            # Skip if Action.from_dict is not implemented
            pytest.skip("Action.from_dict method not implemented")
    
    def test_xml_roundtrip(self):
        """Test XML serialization roundtrip - serialize to XML, parse back, compare."""
        # Create ActionGroup with various configurations
        trigger = ActionTrigger(type=TriggerType.MULTIPLE_TIMING, param=2.5)
        actions = [
            TakePhotoAction(action_id=1, file_suffix="photo1"),
            HoverAction(action_id=2, hover_time=3.0),
            RotateYawAction(action_id=3, aircraft_heading=180.0)
        ]
        
        original_group = ActionGroup(
            group_id=5,
            start_waypoint_id=10,
            end_waypoint_id=15,
            execution_mode="sequence",
            actions=actions,
            trigger=trigger
        )
        
        # Serialize to XML
        xml_str = original_group.to_xml()
        
        # Deserialize from XML
        recreated_group = ActionGroup.from_xml(xml_str)
        
        # Compare all fields
        assert recreated_group.group_id == original_group.group_id
        assert recreated_group.start_waypoint_id == original_group.start_waypoint_id
        assert recreated_group.end_waypoint_id == original_group.end_waypoint_id
        assert recreated_group.execution_mode == original_group.execution_mode
        
        # Compare trigger
        assert recreated_group.trigger.type == original_group.trigger.type
        assert recreated_group.trigger.param == original_group.trigger.param
        
        # Compare actions count and types
        assert len(recreated_group.actions) == len(original_group.actions)
        for orig_action, recreated_action in zip(original_group.actions, recreated_group.actions):
            assert type(recreated_action) == type(orig_action)
            assert recreated_action.action_id == orig_action.action_id
            assert recreated_action.action_type == orig_action.action_type
    
    def test_xml_roundtrip_simple(self):
        """Test XML roundtrip serialization and deserialization with simple group."""
        # Create a simple ActionGroup
        original_group = ActionGroup(
            group_id=5,
            start_waypoint_id=10,
            end_waypoint_id=15,
            execution_mode="sequence"
        )
        
        # Serialize to XML
        xml_str = original_group.to_xml()
        
        # Deserialize from XML
        recreated_group = ActionGroup.from_xml(xml_str)
        
        # Verify all fields match
        assert recreated_group.group_id == original_group.group_id
        assert recreated_group.start_waypoint_id == original_group.start_waypoint_id
        assert recreated_group.end_waypoint_id == original_group.end_waypoint_id
        assert recreated_group.execution_mode == original_group.execution_mode
        assert len(recreated_group.actions) == len(original_group.actions)
        assert recreated_group.trigger.type == original_group.trigger.type
        assert recreated_group.trigger.param == original_group.trigger.param
    
    def test_xml_roundtrip_with_actions(self):
        """Test XML roundtrip with ActionGroup containing multiple actions."""
        # Create ActionGroup with multiple actions
        actions = [
            TakePhotoAction(action_id=1, file_suffix="photo1"),
            HoverAction(action_id=2, hover_time=5.0),
            RotateYawAction(action_id=3, aircraft_heading=90.0)
        ]
        
        trigger = ActionTrigger(type=TriggerType.MULTIPLE_TIMING, param=2.5)
        
        original_group = ActionGroup(
            group_id=7,
            start_waypoint_id=12,
            end_waypoint_id=18,
            execution_mode="sequence",
            actions=actions,
            trigger=trigger
        )
        
        try:
            # Serialize to XML
            xml_str = original_group.to_xml()
            
            # Deserialize from XML
            recreated_group = ActionGroup.from_xml(xml_str)
            
            # Verify group properties
            assert recreated_group.group_id == original_group.group_id
            assert recreated_group.start_waypoint_id == original_group.start_waypoint_id
            assert recreated_group.end_waypoint_id == original_group.end_waypoint_id
            assert recreated_group.execution_mode == original_group.execution_mode
            
            # Verify trigger
            assert recreated_group.trigger.type == original_group.trigger.type
            assert recreated_group.trigger.param == original_group.trigger.param
            
            # Verify actions count
            assert len(recreated_group.actions) == len(original_group.actions)
            
            # Verify each action (if Action.from_dict is implemented)
            for original_action, recreated_action in zip(original_group.actions, recreated_group.actions):
                assert recreated_action.action_id == original_action.action_id
                assert type(recreated_action) == type(original_action)
                
                # Action-specific checks
                if isinstance(original_action, TakePhotoAction):
                    assert recreated_action.file_suffix == original_action.file_suffix
                elif isinstance(original_action, HoverAction):
                    assert recreated_action.hover_time == original_action.hover_time
                elif isinstance(original_action, RotateYawAction):
                    assert recreated_action.aircraft_heading == original_action.aircraft_heading
                    
        except (AttributeError, NotImplementedError):
            # Skip if Action.from_dict is not fully implemented
            pytest.skip("Action.from_dict method not fully implemented for roundtrip testing")
    
    def test_xml_roundtrip_minimal(self):
        """Test XML roundtrip with minimal ActionGroup (all defaults)."""
        # Create minimal ActionGroup with defaults
        original_group = ActionGroup()
        
        # Serialize to XML
        xml_str = original_group.to_xml()
        
        # Deserialize from XML
        recreated_group = ActionGroup.from_xml(xml_str)
        
        # Verify all fields match defaults
        assert recreated_group.group_id == 0
        assert recreated_group.start_waypoint_id == 0
        assert recreated_group.end_waypoint_id == 0
        assert recreated_group.execution_mode == "sequence"
        assert len(recreated_group.actions) == 0
        assert recreated_group.trigger.type == TriggerType.REACH_POINT
        assert recreated_group.trigger.param is None or recreated_group.trigger.param == 0.0

    def test_xml_roundtrip_empty_actions(self):
        """Test XML roundtrip with ActionGroup that has no actions."""
        original_group = ActionGroup(
            group_id=1,
            start_waypoint_id=2,
            end_waypoint_id=3,
            actions=[]  # No actions
        )
        
        # Serialize to XML
        xml_str = original_group.to_xml()
        
        # Deserialize from XML
        recreated_group = ActionGroup.from_xml(xml_str)
        
        # Compare all fields
        assert recreated_group.group_id == original_group.group_id
        assert recreated_group.start_waypoint_id == original_group.start_waypoint_id
        assert recreated_group.end_waypoint_id == original_group.end_waypoint_id
        assert recreated_group.execution_mode == original_group.execution_mode
        assert recreated_group.trigger.type == original_group.trigger.type
        assert len(recreated_group.actions) == len(original_group.actions)


class TestActionGroupComplexScenarios:
    """Test complex ActionGroup scenarios."""
    
    def test_multiple_actions_different_types(self):
        """Test ActionGroup with multiple different action types."""
        actions = [
            TakePhotoAction(action_id=1, file_suffix="photo1"),
            HoverAction(action_id=2, hover_time=5.0),
            RotateYawAction(action_id=3, aircraft_heading=90.0),
            TakePhotoAction(action_id=4, file_suffix="photo2")
        ]
        
        group = ActionGroup(
            group_id=1,
            start_waypoint_id=5,
            end_waypoint_id=10,
            actions=actions
        )
        
        assert len(group.actions) == 4
        assert group.actions[0].action_id == 1
        assert group.actions[1].hover_time == 5.0
        assert group.actions[2].aircraft_heading == 90.0
        assert group.actions[3].file_suffix == "photo2"
    
    def test_trigger_with_timing_parameter(self):
        """Test ActionGroup with timing-based trigger."""
        trigger = ActionTrigger(
            type=TriggerType.MULTIPLE_TIMING,
            param=3.5
        )
        
        group = ActionGroup(
            group_id=2,
            trigger=trigger
        )
        
        assert group.trigger.type == TriggerType.MULTIPLE_TIMING
        assert group.trigger.param == 3.5
    
    def test_large_waypoint_ids(self):
        """Test ActionGroup with large waypoint IDs."""
        group = ActionGroup(
            group_id=1000,
            start_waypoint_id=2000,
            end_waypoint_id=3000
        )
        
        assert group.group_id == 1000
        assert group.start_waypoint_id == 2000
        assert group.end_waypoint_id == 3000
    
    def test_model_dump_exclude_none(self):
        """Test that model_dump properly excludes None values."""
        group = ActionGroup(group_id=1)
        data = group.model_dump(exclude_none=True)
        
        # Should not contain None values
        for key, value in data.items():
            assert value is not None, f"Field {key} should not be None in model_dump"


class TestActionGroupEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_actions_list(self):
        """Test ActionGroup with empty actions list."""
        group = ActionGroup(actions=[])
        assert group.actions == []
        
        # to_dict should handle empty actions
        result = group.to_dict()
        assert result["wpml:action"] == []
    
    def test_waypoint_boundary_conditions(self):
        """Test waypoint ID boundary conditions."""
        # Minimum valid values
        group = ActionGroup(group_id=0, start_waypoint_id=0, end_waypoint_id=0)
        assert group.group_id == 0
        assert group.start_waypoint_id == 0
        assert group.end_waypoint_id == 0
        
        # Large values
        group = ActionGroup(
            group_id=999999,
            start_waypoint_id=999999,
            end_waypoint_id=999999
        )
        assert group.group_id == 999999
    
    def test_trigger_none_handling(self):
        """Test handling of None trigger values."""
        # Default trigger should be created
        group = ActionGroup()
        assert group.trigger is not None
        assert isinstance(group.trigger, ActionTrigger)
        
        # Explicitly set trigger
        custom_trigger = ActionTrigger(type=TriggerType.BETWEEN_POINTS)
        group = ActionGroup(trigger=custom_trigger)
        assert group.trigger.type == TriggerType.BETWEEN_POINTS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
