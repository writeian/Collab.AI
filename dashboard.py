from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, PromptRecord, User, Chat
from access_control import get_current_user, require_login
from sqlalchemy import func
from collections import defaultdict

dashboard = Blueprint('dashboard', __name__)

@dashboard.route("/")
@require_login
def index():
    """Main dashboard showing prompt analytics."""
    user = get_current_user()
    
    # Get all prompt records (for now, show all - later we can add instructor filtering)
    prompt_records = PromptRecord.query.order_by(PromptRecord.timestamp.desc()).all()
    
    # Mode usage statistics
    mode_stats = db.session.query(
        PromptRecord.mode,
        func.count(PromptRecord.id).label('count')
    ).group_by(PromptRecord.mode).all()
    
    # Convert to dictionary for easier template use
    mode_counts = {mode: count for mode, count in mode_stats}
    
    # User statistics
    user_stats = db.session.query(
        PromptRecord.user_id,
        User.display_name,
        func.count(PromptRecord.id).label('prompt_count')
    ).join(User).group_by(PromptRecord.user_id, User.display_name).all()
    
    # Recent prompts (last 20)
    recent_prompts = PromptRecord.query.join(User).join(Chat).order_by(
        PromptRecord.timestamp.desc()
    ).limit(20).all()
    
    return render_template("dashboard/index.html", 
                         user=user,
                         prompt_records=prompt_records,
                         mode_counts=mode_counts,
                         user_stats=user_stats,
                         recent_prompts=recent_prompts)

@dashboard.route("/prompts")
@require_login
def view_prompts():
    """View all prompts with filtering options."""
    user = get_current_user()
    
    # Get filter parameters
    mode_filter = request.args.get('mode', '')
    user_filter = request.args.get('user', '')
    
    # Build query
    query = PromptRecord.query.join(User).join(Chat)
    
    if mode_filter:
        query = query.filter(PromptRecord.mode == mode_filter)
    
    if user_filter:
        query = query.filter(User.username == user_filter)
    
    # Get unique modes and users for filter dropdowns
    modes = db.session.query(PromptRecord.mode).distinct().all()
    users = db.session.query(User.username, User.display_name).distinct().all()
    
    # Get filtered results
    prompts = query.order_by(PromptRecord.timestamp.desc()).all()
    
    return render_template("dashboard/prompts.html",
                         user=user,
                         prompts=prompts,
                         modes=modes,
                         users=users,
                         current_mode=mode_filter,
                         current_user=user_filter) 