from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from models import db, Chat, Message, User, ChatShare
from openai_utils import get_ai_response
from datetime import datetime
import os
from dotenv import load_dotenv
from functools import wraps

# Load environment variables from .env file
load_dotenv()


def create_app():
    app = Flask(__name__)

    # Secret key (needed for sessions & flash messages)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    # SQLite DB lives in project root
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ai_collab.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Helper functions
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to access this page.")
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    def get_current_user():
        if 'user_id' in session:
            return User.query.get(session['user_id'])
        return None

    # ‑‑‑ Routes ‑‑‑

    @app.route("/")
    def index():
        user = get_current_user()
        if user:
            # Show user's chats and shared chats
            owned_chats = Chat.query.filter_by(owner_id=user.id).order_by(Chat.created_at.desc()).all()
            shared_chats = Chat.query.join(ChatShare).filter(ChatShare.user_id == user.id).order_by(Chat.created_at.desc()).all()
            public_chats = Chat.query.filter_by(is_public=True).order_by(Chat.created_at.desc()).limit(10).all()
        else:
            # Show only public chats for anonymous users
            owned_chats = []
            shared_chats = []
            public_chats = Chat.query.filter_by(is_public=True).order_by(Chat.created_at.desc()).limit(10).all()
        
        return render_template("index.html", 
                             user=user, 
                             owned_chats=owned_chats, 
                             shared_chats=shared_chats, 
                             public_chats=public_chats)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"].strip()
            email = request.form["email"].strip()
            display_name = request.form["display_name"].strip()
            password = request.form["password"]
            
            if not all([username, email, display_name, password]):
                flash("All fields are required.")
                return redirect(url_for("register"))
            
            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                flash("Username already exists.")
                return redirect(url_for("register"))
            
            if User.query.filter_by(email=email).first():
                flash("Email already registered.")
                return redirect(url_for("register"))
            
            # Create new user
            user = User(username=username, email=email, display_name=display_name)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Log in the user
            session['user_id'] = user.id
            flash("Registration successful! Welcome to AI Collab.")
            return redirect(url_for("index"))
        
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                flash(f"Welcome back, {user.display_name}!")
                return redirect(url_for("index"))
            else:
                flash("Invalid username or password.")
                return redirect(url_for("login"))
        
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop('user_id', None)
        flash("You have been logged out.")
        return redirect(url_for("index"))

    @app.route("/profile")
    @login_required
    def profile():
        user = get_current_user()
        return render_template("profile.html", user=user)

    @app.route("/create", methods=["GET", "POST"])
    @login_required
    def create_chat():
        user = get_current_user()
        if not user:  # This shouldn't happen due to @login_required, but safety check
            flash("Please log in to create a chat.")
            return redirect(url_for("login"))
            
        if request.method == "POST":
            title = request.form["title"].strip()
            is_public = request.form.get("is_public") == "on"
            
            if not title:
                flash("Chat title is required.")
                return redirect(url_for("create_chat"))

            chat = Chat(title=title, owner_id=user.id, is_public=is_public)
            db.session.add(chat)
            db.session.commit()
            return redirect(url_for("view_chat", chat_id=chat.id))
        
        return render_template("create_chat.html")

    @app.route("/chat/<int:chat_id>", methods=["GET", "POST"])
    def view_chat(chat_id):
        chat = Chat.query.get_or_404(chat_id)
        user = get_current_user()
        
        # Check access permissions
        if not chat.can_access(user):
            flash("You don't have access to this chat.")
            return redirect(url_for("index"))
        
        if request.method == "POST":
            if not user:
                flash("Please log in to send messages.")
                return redirect(url_for("login"))
            
            content = request.form["content"].strip()
            if content:
                # save user message
                user_msg = Message(chat_id=chat.id, user_id=user.id, role="user", content=content)
                db.session.add(user_msg)
                db.session.commit()

                # ask GPT‑4o and store assistant reply
                ai_content = get_ai_response(chat)
                ai_msg = Message(chat_id=chat.id, role="assistant", content=ai_content)
                db.session.add(ai_msg)
                db.session.commit()
            return redirect(url_for("view_chat", chat_id=chat.id))

        messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp).all()
        return render_template("view_chat.html", chat=chat, messages=messages, user=user)

    @app.route("/edit/<int:chat_id>", methods=["GET", "POST"])
    @login_required
    def edit_chat(chat_id):
        chat = Chat.query.get_or_404(chat_id)
        user = get_current_user()
        
        if not chat.can_edit(user):
            flash("You can only edit your own chats.")
            return redirect(url_for("view_chat", chat_id=chat.id))

        if request.method == "POST":
            chat.title = request.form["title"].strip()
            chat.is_public = request.form.get("is_public") == "on"
            db.session.commit()
            flash("Chat updated successfully.")
            return redirect(url_for("view_chat", chat_id=chat.id))
        
        return render_template("edit_chat.html", chat=chat)

    @app.route("/delete/<int:chat_id>", methods=["POST"])
    @login_required
    def delete_chat(chat_id):
        chat = Chat.query.get_or_404(chat_id)
        user = get_current_user()
        
        if not chat.can_edit(user):
            flash("You can only delete your own chats.")
            return redirect(url_for("view_chat", chat_id=chat.id))

        # Delete the chat (messages and shares will be deleted due to cascade)
        db.session.delete(chat)
        db.session.commit()
        flash("Chat deleted successfully.")
        return redirect(url_for("index"))

    @app.route("/share/<int:chat_id>", methods=["GET", "POST"])
    @login_required
    def share_chat(chat_id):
        chat = Chat.query.get_or_404(chat_id)
        user = get_current_user()
        
        if not user:  # This shouldn't happen due to @login_required, but safety check
            flash("Please log in to share a chat.")
            return redirect(url_for("login"))
        
        if not chat.can_edit(user):
            flash("You can only share your own chats.")
            return redirect(url_for("view_chat", chat_id=chat.id))

        if request.method == "POST":
            username = request.form["username"].strip()
            can_edit = request.form.get("can_edit") == "on"
            
            target_user = User.query.filter_by(username=username).first()
            if not target_user:
                flash("User not found.")
                return redirect(url_for("share_chat", chat_id=chat.id))
            
            if target_user.id == user.id:
                flash("You cannot share a chat with yourself.")
                return redirect(url_for("share_chat", chat_id=chat.id))
            
            # Check if already shared
            existing_share = ChatShare.query.filter_by(chat_id=chat.id, user_id=target_user.id).first()
            if existing_share:
                flash("Chat is already shared with this user.")
                return redirect(url_for("share_chat", chat_id=chat.id))
            
            # Create share
            share = ChatShare(chat_id=chat.id, user_id=target_user.id, can_edit=can_edit)
            db.session.add(share)
            db.session.commit()
            flash(f"Chat shared with {target_user.display_name} successfully.")
            return redirect(url_for("view_chat", chat_id=chat.id))
        
        return render_template("share_chat.html", chat=chat)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
