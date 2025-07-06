from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy instance is created here so it can be imported by app.py
# without causing circular-import issues.
db = SQLAlchemy()

class User(db.Model):
    """A registered user of the application."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    owned_chats = db.relationship('Chat', backref='owner', lazy=True, foreign_keys='Chat.owner_id')
    shared_chats = db.relationship('ChatShare', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"

class Chat(db.Model):
    """A conversation that can be shared between users."""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan')
    shares = db.relationship('ChatShare', backref='chat', lazy=True, cascade='all, delete-orphan')
    
    def can_access(self, user):
        """Check if a user can access this chat."""
        if not user:
            return self.is_public
        return (user.id == self.owner_id or 
                self.is_public or 
                any(share.user_id == user.id for share in self.shares))
    
    def can_edit(self, user):
        """Check if a user can edit this chat."""
        return user and user.id == self.owner_id
    
    def __repr__(self):
        return f"<Chat {self.id} {self.title!r}>"

class ChatShare(db.Model):
    """Represents a user's access to a shared chat."""
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    can_edit = db.Column(db.Boolean, default=False, nullable=False)
    shared_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (db.UniqueConstraint('chat_id', 'user_id', name='unique_chat_user'),)
    
    def __repr__(self):
        return f"<ChatShare chat_id={self.chat_id} user_id={self.user_id}>"

class Message(db.Model):
    """A single turn in the conversation (user or assistant)."""
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # null for assistant messages
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref='messages')
    
    def __repr__(self):
        return f"<Message {self.id} role={self.role}>"