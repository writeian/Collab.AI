"""Access control utilities for chat permissions.

This module provides helper methods and decorators for checking
user permissions on chats and enforcing access control.
"""
from functools import wraps
from flask import abort, flash, redirect, url_for, session
from models import Chat, User, ChatShare


def get_current_user():
    """Get the currently logged-in user from session."""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def can_access_chat(user, chat):
    """Check if a user can access a chat.
    
    Args:
        user: User object or None for anonymous users
        chat: Chat object to check access for
        
    Returns:
        bool: True if user can access the chat, False otherwise
    """
    if not chat:
        return False
        
    # Public chats can be accessed by anyone
    if chat.is_public:
        return True
        
    # Private chats require authentication
    if not user:
        return False
        
    # Chat owner can always access
    if chat.owner_id == user.id:
        return True
        
    # Check if user has been shared the chat
    share = ChatShare.query.filter_by(
        chat_id=chat.id, 
        user_id=user.id
    ).first()
    
    return share is not None


def can_edit_chat(user, chat):
    """Check if a user can edit a chat.
    
    Args:
        user: User object (must be authenticated)
        chat: Chat object to check edit permissions for
        
    Returns:
        bool: True if user can edit the chat, False otherwise
    """
    if not user or not chat:
        return False
        
    # Chat owner can always edit
    if chat.owner_id == user.id:
        return True
        
    # Check if user has edit permissions via sharing
    share = ChatShare.query.filter_by(
        chat_id=chat.id, 
        user_id=user.id,
        can_edit=True
    ).first()
    
    return share is not None


def can_delete_chat(user, chat):
    """Check if a user can delete a chat.
    
    Args:
        user: User object (must be authenticated)
        chat: Chat object to check delete permissions for
        
    Returns:
        bool: True if user can delete the chat, False otherwise
    """
    if not user or not chat:
        return False
        
    # Only chat owner can delete
    return chat.owner_id == user.id


def require_login(f):
    """Decorator to require user authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("Please log in to access this page.")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def require_chat_access(f):
    """Decorator to require chat access permissions."""
    @wraps(f)
    def decorated_function(chat_id, *args, **kwargs):
        chat = Chat.query.get_or_404(chat_id)
        user = get_current_user()
        
        if not can_access_chat(user, chat):
            flash("You don't have access to this chat.")
            return redirect(url_for('chat.index'))
            
        return f(chat_id, *args, **kwargs)
    return decorated_function


def require_chat_edit(f):
    """Decorator to require chat edit permissions."""
    @wraps(f)
    def decorated_function(chat_id, *args, **kwargs):
        chat = Chat.query.get_or_404(chat_id)
        user = get_current_user()
        
        if not user:
            flash("Please log in to edit chats.")
            return redirect(url_for('auth.login'))
            
        if not can_edit_chat(user, chat):
            flash("You can only edit your own chats or chats shared with edit permissions.")
            return redirect(url_for('chat.view_chat', chat_id=chat_id))
            
        return f(chat_id, *args, **kwargs)
    return decorated_function


def require_chat_owner(f):
    """Decorator to require chat ownership (for delete operations)."""
    @wraps(f)
    def decorated_function(chat_id, *args, **kwargs):
        chat = Chat.query.get_or_404(chat_id)
        user = get_current_user()
        
        if not user:
            flash("Please log in to manage chats.")
            return redirect(url_for('auth.login'))
            
        if not can_delete_chat(user, chat):
            flash("You can only delete your own chats.")
            return redirect(url_for('chat.view_chat', chat_id=chat_id))
            
        return f(chat_id, *args, **kwargs)
    return decorated_function 