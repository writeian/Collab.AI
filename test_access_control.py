"""Unit tests for access control module."""

import pytest
from unittest.mock import Mock, patch
from access_control import (
    can_access_chat,
    can_edit_chat,
    can_delete_chat,
    get_current_user
)


class TestAccessControl:
    """Test cases for access control functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.user = Mock()
        self.user.id = 1
        self.user.username = "testuser"
        
        self.other_user = Mock()
        self.other_user.id = 2
        self.other_user.username = "otheruser"
        
        self.chat = Mock()
        self.chat.id = 1
        self.chat.owner_id = 1
        self.chat.is_public = False
        
        self.public_chat = Mock()
        self.public_chat.id = 2
        self.public_chat.owner_id = 2
        self.public_chat.is_public = True
        
        self.share = Mock()
        self.share.user_id = 1
        self.share.can_edit = True
    
    def test_can_access_chat_public(self):
        """Test that public chats can be accessed by anyone."""
        assert can_access_chat(None, self.public_chat) == True
        assert can_access_chat(self.user, self.public_chat) == True
        assert can_access_chat(self.other_user, self.public_chat) == True
    
    def test_can_access_chat_owner(self):
        """Test that chat owner can always access their chat."""
        assert can_access_chat(self.user, self.chat) == True
    
    def test_can_access_chat_anonymous_private(self):
        """Test that anonymous users cannot access private chats."""
        assert can_access_chat(None, self.chat) == False
    
    def test_can_access_chat_shared(self):
        """Test that shared users can access chats."""
        with patch('access_control.ChatShare') as mock_chat_share:
            mock_chat_share.query.filter_by.return_value.first.return_value = self.share
            assert can_access_chat(self.user, self.chat) == True
    
    def test_can_access_chat_not_shared(self):
        """Test that non-shared users cannot access private chats."""
        with patch('access_control.ChatShare') as mock_chat_share:
            mock_chat_share.query.filter_by.return_value.first.return_value = None
            assert can_access_chat(self.other_user, self.chat) == False
    
    def test_can_edit_chat_owner(self):
        """Test that chat owner can always edit their chat."""
        assert can_edit_chat(self.user, self.chat) == True
    
    def test_can_edit_chat_anonymous(self):
        """Test that anonymous users cannot edit chats."""
        assert can_edit_chat(None, self.chat) == False
    
    def test_can_edit_chat_shared_with_edit(self):
        """Test that users shared with edit permissions can edit."""
        with patch('access_control.ChatShare') as mock_chat_share:
            mock_chat_share.query.filter_by.return_value.first.return_value = self.share
            assert can_edit_chat(self.user, self.chat) == True
    
    def test_can_edit_chat_shared_without_edit(self):
        """Test that users shared without edit permissions cannot edit."""
        share_no_edit = Mock()
        share_no_edit.user_id = 1
        share_no_edit.can_edit = False
        
        with patch('access_control.ChatShare') as mock_chat_share:
            mock_chat_share.query.filter_by.return_value.first.return_value = share_no_edit
            assert can_edit_chat(self.user, self.chat) == False
    
    def test_can_edit_chat_not_shared(self):
        """Test that non-shared users cannot edit chats."""
        with patch('access_control.ChatShare') as mock_chat_share:
            mock_chat_share.query.filter_by.return_value.first.return_value = None
            assert can_edit_chat(self.other_user, self.chat) == False
    
    def test_can_delete_chat_owner(self):
        """Test that only chat owner can delete their chat."""
        assert can_delete_chat(self.user, self.chat) == True
        assert can_delete_chat(self.other_user, self.chat) == False
        assert can_delete_chat(None, self.chat) == False
    
    def test_can_delete_chat_shared_user(self):
        """Test that shared users cannot delete chats."""
        with patch('access_control.ChatShare') as mock_chat_share:
            mock_chat_share.query.filter_by.return_value.first.return_value = self.share
            assert can_delete_chat(self.user, self.chat) == True  # Still owner
    
    def test_can_access_chat_none_chat(self):
        """Test that None chat returns False."""
        assert can_access_chat(self.user, None) == False
        assert can_edit_chat(self.user, None) == False
        assert can_delete_chat(self.user, None) == False
    
    def test_get_current_user_with_session(self):
        """Test get_current_user when user is in session."""
        with patch('access_control.session') as mock_session:
            mock_session.__contains__.return_value = True
            mock_session.__getitem__.return_value = 1
            
            with patch('access_control.User') as mock_user:
                mock_user.query.get.return_value = self.user
                result = get_current_user()
                assert result == self.user
    
    def test_get_current_user_no_session(self):
        """Test get_current_user when no user in session."""
        with patch('access_control.session') as mock_session:
            mock_session.__contains__.return_value = False
            result = get_current_user()
            assert result is None


class TestAccessControlEdgeCases:
    """Test edge cases for access control."""
    
    def test_chat_with_no_owner(self):
        """Test access control with chat that has no owner."""
        user = Mock()
        user.id = 1
        
        chat = Mock()
        chat.owner_id = None
        chat.is_public = False
        
        # Should handle gracefully
        assert can_access_chat(user, chat) == False
        assert can_edit_chat(user, chat) == False
        assert can_delete_chat(user, chat) == False
    
    def test_user_with_no_id(self):
        """Test access control with user that has no id."""
        user = Mock()
        user.id = None
        
        chat = Mock()
        chat.owner_id = 1
        chat.is_public = False
        
        # Should handle gracefully
        assert can_access_chat(user, chat) == False
        assert can_edit_chat(user, chat) == False
        assert can_delete_chat(user, chat) == False


if __name__ == "__main__":
    pytest.main([__file__]) 