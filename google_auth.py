from flask import Blueprint, request, redirect, url_for, session, flash
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from models import db, User, GoogleAuth
from access_control import get_current_user, require_login
import os
from datetime import datetime, timedelta
import json

google_auth = Blueprint('google_auth', __name__)

# OAuth 2.0 scopes needed for Google Docs API
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.readonly'
]

@google_auth.route('/connect')
@require_login
def connect_google():
    """Initiate Google OAuth flow."""
    user = get_current_user()
    
    # Check if user already has Google auth
    existing_auth = GoogleAuth.query.filter_by(user_id=user.id).first()
    if existing_auth:
        flash("You already have Google Docs connected.")
        return redirect(url_for('auth.profile'))
    
    # Create OAuth flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
            }
        },
        scopes=SCOPES
    )
    
    flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    # Store user ID in session for callback
    session['google_auth_user_id'] = user.id
    
    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    return redirect(authorization_url)

@google_auth.route('/callback')
def google_callback():
    """Handle Google OAuth callback."""
    user_id = session.get('google_auth_user_id')
    if not user_id:
        flash("Authentication session expired. Please try again.")
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    if not user:
        flash("User not found.")
        return redirect(url_for('auth.login'))
    
    # Create OAuth flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    # Exchange authorization code for tokens
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    
    # Calculate token expiry
    expiry = None
    if credentials.expiry:
        expiry = credentials.expiry
    
    # Save tokens to database
    google_auth = GoogleAuth(
        user_id=user.id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_expiry=expiry
    )
    
    db.session.add(google_auth)
    db.session.commit()
    
    # Clear session
    session.pop('google_auth_user_id', None)
    
    flash("Google Docs successfully connected!")
    return redirect(url_for('auth.profile'))

@google_auth.route('/disconnect')
@require_login
def disconnect_google():
    """Disconnect Google account."""
    user = get_current_user()
    google_auth = GoogleAuth.query.filter_by(user_id=user.id).first()
    
    if google_auth:
        db.session.delete(google_auth)
        db.session.commit()
        flash("Google Docs disconnected successfully.")
    else:
        flash("No Google account connected.")
    
    return redirect(url_for('auth.profile'))

def get_google_credentials(user_id):
    """Get valid Google credentials for a user."""
    google_auth = GoogleAuth.query.filter_by(user_id=user_id).first()
    if not google_auth:
        return None
    
    credentials = Credentials(
        token=google_auth.access_token,
        refresh_token=google_auth.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES
    )
    
    # Refresh token if expired
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        
        # Update stored tokens
        google_auth.access_token = credentials.token
        google_auth.token_expiry = credentials.expiry
        db.session.commit()
    
    return credentials

def get_google_docs_service(user_id):
    """Get Google Docs API service for a user."""
    credentials = get_google_credentials(user_id)
    if not credentials:
        return None
    
    return build('docs', 'v1', credentials=credentials)

def get_google_drive_service(user_id):
    """Get Google Drive API service for a user."""
    credentials = get_google_credentials(user_id)
    if not credentials:
        return None
    
    return build('drive', 'v3', credentials=credentials) 