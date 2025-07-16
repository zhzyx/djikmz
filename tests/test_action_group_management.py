import pytest
from djikmz.model.action_group import ActionGroup, ActionTrigger, TriggerType
from djikmz.model.action.camera_actions import TakePhotoAction
from djikmz.model.action.movement_actions import HoverAction
from djikmz.model.action.gimbal_actions import GimbalRotateAction


class TestActionGroupManagement:
    """Test action management functionality in ActionGroup."""
    
    def test_add_action_with_auto_id(self):
        """Test adding actions with automatic ID assignment."""
        group = ActionGroup(group_id=1)
        
        # Add first action
        action1 = TakePhotoAction(action_id=999)  # ID should be overridden
        group.add_action(action1, auto_id=True)
        
        assert len(group.actions) == 1
        assert group.actions[0].action_id == 1
        
        # Add second action
        action2 = HoverAction(action_id=888, hover_time=2.0)
        group.add_action(action2, auto_id=True)
        
        assert len(group.actions) == 2
        assert group.actions[1].action_id == 2
    
    def test_add_action_without_auto_id(self):
        """Test adding actions without automatic ID assignment."""
        group = ActionGroup(group_id=1)
        
        action = TakePhotoAction(action_id=5)
        group.add_action(action, auto_id=False)
        
        assert len(group.actions) == 1
        assert group.actions[0].action_id == 5
    
    def test_insert_action_at_beginning(self):
        """Test inserting action at the beginning."""
        group = ActionGroup(group_id=1)
        
        # Add initial actions
        group.add_action(TakePhotoAction(action_id=1))
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        
        # Insert at beginning
        new_action = GimbalRotateAction(action_id=999)
        group.insert_action(0, new_action, auto_renumber=True)
        
        assert len(group.actions) == 3
        # Check that all actions are renumbered
        assert group.actions[0].action_id == 1  # GimbalRotateAction
        assert group.actions[1].action_id == 2  # TakePhotoAction
        assert group.actions[2].action_id == 3  # HoverAction
        assert isinstance(group.actions[0], GimbalRotateAction)
    
    def test_insert_action_in_middle(self):
        """Test inserting action in the middle."""
        group = ActionGroup(group_id=1)
        
        # Add initial actions
        group.add_action(TakePhotoAction(action_id=1))
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        
        # Insert in middle
        new_action = GimbalRotateAction(action_id=999)
        group.insert_action(1, new_action, auto_renumber=True)
        
        assert len(group.actions) == 3
        assert isinstance(group.actions[0], TakePhotoAction)
        assert isinstance(group.actions[1], GimbalRotateAction)
        assert isinstance(group.actions[2], HoverAction)
        # Check renumbering
        assert group.actions[0].action_id == 1
        assert group.actions[1].action_id == 2
        assert group.actions[2].action_id == 3
    
    def test_insert_action_invalid_index(self):
        """Test inserting action with invalid index."""
        group = ActionGroup(group_id=1)
        group.add_action(TakePhotoAction(action_id=1))
        
        action = HoverAction(action_id=2, hover_time=1.0)
        
        with pytest.raises(ValueError, match="Index .* out of range"):
            group.insert_action(-1, action)
        
        with pytest.raises(ValueError, match="Index .* out of range"):
            group.insert_action(5, action)
    
    def test_remove_action_by_id(self):
        """Test removing action by ID."""
        group = ActionGroup(group_id=1)
        
        # Add actions
        group.add_action(TakePhotoAction(action_id=1))
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        group.add_action(GimbalRotateAction(action_id=3))
        
        # Remove middle action
        result = group.remove_action(2, auto_renumber=True)
        
        assert result is True
        assert len(group.actions) == 2
        assert isinstance(group.actions[0], TakePhotoAction)
        assert isinstance(group.actions[1], GimbalRotateAction)
        # Check renumbering
        assert group.actions[0].action_id == 1
        assert group.actions[1].action_id == 2
    
    def test_remove_action_by_id_not_found(self):
        """Test removing action with non-existent ID."""
        group = ActionGroup(group_id=1)
        group.add_action(TakePhotoAction(action_id=1))
        
        result = group.remove_action(999)
        
        assert result is False
        assert len(group.actions) == 1
    
    def test_remove_action_at_index(self):
        """Test removing action by index."""
        group = ActionGroup(group_id=1)
        
        # Add actions
        group.add_action(TakePhotoAction(action_id=1))
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        group.add_action(GimbalRotateAction(action_id=3))
        
        # Remove first action
        removed = group.remove_action_at(0, auto_renumber=True)
        
        assert isinstance(removed, TakePhotoAction)
        assert len(group.actions) == 2
        assert isinstance(group.actions[0], HoverAction)
        assert isinstance(group.actions[1], GimbalRotateAction)
        # Check renumbering
        assert group.actions[0].action_id == 1
        assert group.actions[1].action_id == 2
    
    def test_remove_action_at_invalid_index(self):
        """Test removing action with invalid index."""
        group = ActionGroup(group_id=1)
        group.add_action(TakePhotoAction(action_id=1))
        
        with pytest.raises(IndexError, match="Index .* out of range"):
            group.remove_action_at(-1)
        
        with pytest.raises(IndexError, match="Index .* out of range"):
            group.remove_action_at(5)
    
    def test_move_action(self):
        """Test moving action from one position to another."""
        group = ActionGroup(group_id=1)
        
        # Add actions
        group.add_action(TakePhotoAction(action_id=1))
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        group.add_action(GimbalRotateAction(action_id=3))
        
        # Move first action to last position
        group.move_action(0, 2, auto_renumber=True)
        
        assert len(group.actions) == 3
        assert isinstance(group.actions[0], HoverAction)
        assert isinstance(group.actions[1], GimbalRotateAction)
        assert isinstance(group.actions[2], TakePhotoAction)
        # Check renumbering
        assert group.actions[0].action_id == 1
        assert group.actions[1].action_id == 2
        assert group.actions[2].action_id == 3
    
    def test_move_action_invalid_indices(self):
        """Test moving action with invalid indices."""
        group = ActionGroup(group_id=1)
        group.add_action(TakePhotoAction(action_id=1))
        
        with pytest.raises(IndexError, match="From index .* out of range"):
            group.move_action(-1, 0)
        
        with pytest.raises(IndexError, match="To index .* out of range"):
            group.move_action(0, 5)
    
    def test_clear_actions(self):
        """Test clearing all actions."""
        group = ActionGroup(group_id=1)
        
        # Add actions
        group.add_action(TakePhotoAction(action_id=1))
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        
        group.clear_actions()
        
        assert len(group.actions) == 0
        assert group.action_count == 0
    
    def test_get_action_by_id(self):
        """Test getting action by ID."""
        group = ActionGroup(group_id=1)
        
        action1 = TakePhotoAction(action_id=1)
        action2 = HoverAction(action_id=2, hover_time=1.0)
        group.add_action(action1)
        group.add_action(action2)
        
        found_action = group.get_action_by_id(2)
        assert found_action is not None
        assert isinstance(found_action, HoverAction)
        assert found_action.action_id == 2
        
        not_found = group.get_action_by_id(999)
        assert not_found is None
    
    def test_action_count_property(self):
        """Test action_count property."""
        group = ActionGroup(group_id=1)
        
        assert group.action_count == 0
        
        group.add_action(TakePhotoAction(action_id=1))
        assert group.action_count == 1
        
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        assert group.action_count == 2
        
        group.remove_action(1)
        assert group.action_count == 1
    
    def test_next_action_id_property(self):
        """Test next_action_id property."""
        group = ActionGroup(group_id=1)
        
        assert group.next_action_id == 1
        
        group.add_action(TakePhotoAction(action_id=1))
        assert group.next_action_id == 2
        
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        assert group.next_action_id == 3
    
    def test_auto_renumber_disabled(self):
        """Test operations with auto-renumbering disabled."""
        group = ActionGroup(group_id=1)
        
        # Add actions
        group.add_action(TakePhotoAction(action_id=1))
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        group.add_action(GimbalRotateAction(action_id=3))
        
        # Remove middle action without renumbering
        group.remove_action(2, auto_renumber=False)
        
        assert len(group.actions) == 2
        assert group.actions[0].action_id == 1
        assert group.actions[1].action_id == 3  # Not renumbered
    
    def test_complex_action_management_scenario(self):
        """Test complex scenario with multiple operations."""
        group = ActionGroup(group_id=1)
        
        # Build initial action sequence
        group.add_action(TakePhotoAction(action_id=1))
        group.add_action(HoverAction(action_id=2, hover_time=1.0))
        group.add_action(TakePhotoAction(action_id=3))
        
        # Insert a gimbal action between the photos
        group.insert_action(1, GimbalRotateAction(action_id=999))
        
        # Verify sequence and IDs
        assert len(group.actions) == 4
        assert isinstance(group.actions[0], TakePhotoAction)
        assert isinstance(group.actions[1], GimbalRotateAction)
        assert isinstance(group.actions[2], HoverAction)
        assert isinstance(group.actions[3], TakePhotoAction)
        
        # Check all actions are properly numbered
        for i, action in enumerate(group.actions, 1):
            assert action.action_id == i
        
        # Move the last photo to the beginning
        group.move_action(3, 0)
        
        # Verify new sequence
        assert isinstance(group.actions[0], TakePhotoAction)
        assert isinstance(group.actions[1], TakePhotoAction)
        assert isinstance(group.actions[2], GimbalRotateAction)
        assert isinstance(group.actions[3], HoverAction)
        
        # Check renumbering
        for i, action in enumerate(group.actions, 1):
            assert action.action_id == i


class TestActionGroupManagementEdgeCases:
    """Test edge cases for action management."""
    
    def test_renumber_with_empty_actions(self):
        """Test renumbering with no actions."""
        group = ActionGroup(group_id=1)
        group._renumber_actions()  # Should not raise
        assert len(group.actions) == 0
    
    def test_operations_on_empty_group(self):
        """Test operations on empty action group."""
        group = ActionGroup(group_id=1)
        
        # These should work without issues
        assert group.get_action_by_id(1) is None
        assert group.remove_action(1) is False
        group.clear_actions()  # Should not raise
        
        # These should raise appropriate errors
        with pytest.raises(IndexError):
            group.remove_action_at(0)
