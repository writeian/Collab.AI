from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User
from access_control import get_current_user, require_login

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        display_name = request.form["display_name"].strip()
        password = request.form["password"]
        
        if not all([username, email, display_name, password]):
            flash("All fields are required.")
            return redirect(url_for("auth.register"))
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("auth.register"))
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("auth.register"))
        
        # Create new user
        user = User(username=username, email=email, display_name=display_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Log in the user
        session['user_id'] = user.id
        flash("Registration successful! Welcome to AI Collab.")
        return redirect(url_for("chat.index"))
    
    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f"Welcome back, {user.display_name}!")
            return redirect(url_for("chat.index"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("auth.login"))
    
    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for("chat.index"))

@auth.route("/profile")
@require_login
def profile():
    user = get_current_user()
    return render_template("profile.html", user=user) 