from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import db, Chat, Message, User, ChatShare, PromptRecord
from openai_utils import get_ai_response, MODES
from access_control import (
    get_current_user, 
    require_login, 
    require_chat_access, 
    require_chat_edit, 
    require_chat_owner,
    can_access_chat,
    can_edit_chat
)
from google_docs import validate_google_docs_url, get_document_content

chat = Blueprint('chat', __name__)

@chat.route("/")
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
                         public_chats=public_chats,
                         modes=MODES)

@chat.route("/create", methods=["GET", "POST"])
@require_login
def create_chat():
    user = get_current_user()
        
    if request.method == "POST":
        title = request.form["title"].strip()
        mode = request.form.get("mode", "explore")
        is_public = request.form.get("is_public") == "on"
        google_doc_url = request.form.get("google_doc_url", "").strip()
        
        if not title:
            flash("Chat title is required.")
            return redirect(url_for("chat.create_chat"))

        # Validate Google Doc URL if provided
        if google_doc_url:
            is_valid, doc_id_or_error = validate_google_docs_url(google_doc_url)
            if not is_valid:
                flash(f"Google Doc URL error: {doc_id_or_error}")
                return redirect(url_for("chat.create_chat"))

        chat_obj = Chat(title=title, owner_id=user.id, mode=mode, is_public=is_public)
        db.session.add(chat_obj)
        db.session.commit()
        
        # If Google Doc URL provided, import the content
        if google_doc_url:
            doc_id = doc_id_or_error  # This is the doc_id from validation
            content, error = get_document_content(doc_id)
            
            if error:
                flash(f"Could not access Google Doc: {error}")
                return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))
            
            if content:
                # Add the Google Doc content as the first user message
                doc_message = Message(
                    chat_id=chat_obj.id, 
                    user_id=user.id, 
                    role="user", 
                    content=f"[Google Doc Content]\n\n{content}"
                )
                db.session.add(doc_message)
                
                # Get AI response to the imported content
                ai_content = get_ai_response(chat_obj)
                ai_msg = Message(chat_id=chat_obj.id, role="assistant", content=ai_content)
                db.session.add(ai_msg)
                db.session.commit()
                
                flash("Google Doc content imported successfully!")
        
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))
    
    return render_template("create_chat.html", modes=MODES)

@chat.route("/chat/<int:chat_id>", methods=["GET", "POST"])
@require_chat_access
def view_chat(chat_id):
    chat_obj = Chat.query.get_or_404(chat_id)
    user = get_current_user()
    
    if request.method == "POST":
        if not user:
            flash("Please log in to send messages.")
            return redirect(url_for("auth.login"))
        
        content = request.form["content"].strip()
        if content:
            # save user message
            user_msg = Message(chat_id=chat_obj.id, user_id=user.id, role="user", content=content)
            db.session.add(user_msg)
            
            # Record the prompt for dashboard analytics
            prompt_record = PromptRecord(
                user_id=user.id,
                chat_id=chat_obj.id,
                mode=chat_obj.mode,
                prompt_content=content
            )
            db.session.add(prompt_record)
            db.session.commit()

            # ask GPT‑4o and store assistant reply
            ai_content = get_ai_response(chat_obj)
            ai_msg = Message(chat_id=chat_obj.id, role="assistant", content=ai_content)
            db.session.add(ai_msg)
            db.session.commit()
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))

    messages = Message.query.filter_by(chat_id=chat_obj.id).order_by(Message.timestamp).all()
    return render_template("view_chat.html", chat=chat_obj, messages=messages, user=user, modes=MODES)

@chat.route("/edit/<int:chat_id>", methods=["GET", "POST"])
@require_chat_edit
def edit_chat(chat_id):
    chat_obj = Chat.query.get_or_404(chat_id)
    
    if request.method == "POST":
        chat_obj.title = request.form["title"].strip()
        chat_obj.mode = request.form.get("mode", "explore")
        chat_obj.is_public = request.form.get("is_public") == "on"
        db.session.commit()
        flash("Chat updated successfully.")
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))
    
    return render_template("edit_chat.html", chat=chat_obj, modes=MODES)

@chat.route("/delete/<int:chat_id>", methods=["GET", "POST"])
@require_chat_owner
def delete_chat(chat_id):
    chat_obj = Chat.query.get_or_404(chat_id)
    
    if request.method == "POST":
        # Delete the chat (messages and shares will be deleted due to cascade)
        db.session.delete(chat_obj)
        db.session.commit()
        flash("Chat deleted successfully.")
        return redirect(url_for("chat.index"))
    
    return render_template("delete_chat.html", chat=chat_obj)

@chat.route("/share/<int:chat_id>", methods=["GET", "POST"])
@require_chat_edit
def share_chat(chat_id):
    chat_obj = Chat.query.get_or_404(chat_id)
    user = get_current_user()

    if request.method == "POST":
        username = request.form["username"].strip()
        can_edit = request.form.get("can_edit") == "on"
        
        target_user = User.query.filter_by(username=username).first()
        if not target_user:
            flash("User not found.")
            return redirect(url_for("chat.share_chat", chat_id=chat_obj.id))
        
        if target_user.id == user.id:
            flash("You cannot share a chat with yourself.")
            return redirect(url_for("chat.share_chat", chat_id=chat_obj.id))
        
        # Check if already shared
        existing_share = ChatShare.query.filter_by(chat_id=chat_obj.id, user_id=target_user.id).first()
        if existing_share:
            flash("Chat is already shared with this user.")
            return redirect(url_for("chat.share_chat", chat_id=chat_obj.id))
        
        # Create share
        share = ChatShare(chat_id=chat_obj.id, user_id=target_user.id, can_edit=can_edit)
        db.session.add(share)
        db.session.commit()
        flash(f"Chat shared with {target_user.display_name} successfully.")
        return redirect(url_for("chat.view_chat", chat_id=chat_obj.id))
    
    return render_template("share_chat.html", chat=chat_obj) 