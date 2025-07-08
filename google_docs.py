import re
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Docs API service account credentials
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service-account-key.json')

def get_google_docs_service():
    """Get Google Docs API service using service account."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('docs', 'v1', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error setting up Google Docs service: {e}")
        return None

def extract_document_id(url):
    """Extract document ID from Google Docs URL."""
    # Pattern for Google Docs URLs
    patterns = [
        r'docs\.google\.com/document/d/([a-zA-Z0-9_-]+)',
        r'docs\.google\.com/document/d/([a-zA-Z0-9_-]+)/edit',
        r'docs\.google\.com/document/d/([a-zA-Z0-9_-]+)/view'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_document_content(doc_id):
    """Get document content from Google Docs API (main document only)."""
    service = get_google_docs_service()
    if not service:
        return None, "Google Docs service not configured"
    
    try:
        # Get document content (main document only)
        document = service.documents().get(documentId=doc_id).execute()
        
        # Extract text content from the document
        content = []
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for para_element in element['paragraph']['elements']:
                    if 'textRun' in para_element:
                        content.append(para_element['textRun']['content'])
        
        return ''.join(content).strip(), None
        
    except HttpError as e:
        if e.resp.status == 404:
            return None, "Document not found or not shared with the service account"
        elif e.resp.status == 403:
            return None, "Access denied. Please share the document with the service account"
        else:
            return None, f"Error accessing document: {e}"
    except Exception as e:
        return None, f"Error: {e}"

def validate_google_docs_url(url):
    """Validate if the URL is a valid Google Docs URL."""
    if not url:
        return False, "URL is required"
    
    doc_id = extract_document_id(url)
    if not doc_id:
        return False, "Invalid Google Docs URL format"
    
    return True, doc_id 