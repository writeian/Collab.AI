from flask import Flask
from models import db
import os
from dotenv import load_dotenv

# Import Blueprints
from auth import auth
from chat import chat
from dashboard import dashboard
from google_auth import google_auth

# Load environment variables from .env file
load_dotenv()


def create_app():
    app = Flask(__name__)

    # Secret key (needed for sessions & flash messages)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    # SQLite DB lives in project root
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ai_collab.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    # Register Blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(chat, url_prefix='/chat')
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    app.register_blueprint(google_auth, url_prefix='/auth/google')
    
    # Redirect root to chat index
    @app.route('/')
    def root():
        from flask import redirect, url_for
        return redirect(url_for('chat.index'))

    # Admin route to view users
    @app.route('/admin/users')
    def admin_users():
        from models import User
        from flask import render_template
        users = User.query.all()
        return render_template('admin_users.html', users=users)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
