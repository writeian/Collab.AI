# Google Docs Integration Setup

This guide explains how to set up the simplified Google Docs integration for AI Collab.

## Overview

The Google Docs integration allows students to share their documents with AI Collab and get intelligent feedback. Students simply need to:

1. Share their Google Doc with the service account
2. Paste the document URL into AI Collab
3. Get AI analysis and feedback

## Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Docs API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Docs API"
   - Click "Enable"

### 2. Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the details:
   - Name: `ai-collab-docs`
   - Description: `Service account for AI Collab Google Docs integration`
4. Click "Create and Continue"
5. Skip role assignment (we'll handle permissions manually)
6. Click "Done"

### 3. Generate Service Account Key

1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" format
5. Download the key file
6. Rename it to `service-account-key.json`
7. Place it in your AI Collab project root directory

### 4. Configure Environment Variables

Add to your `.env` file:
```env
GOOGLE_SERVICE_ACCOUNT_FILE=service-account-key.json
```

### 5. Get Service Account Email

The service account email will be in the format:
`ai-collab-docs@your-project-id.iam.gserviceaccount.com`

You can find this in the downloaded JSON file under the `client_email` field.

## Student Instructions

### How Students Share Documents

1. **Open their Google Doc**
2. **Click "Share"** in the top right corner
3. **Add the service account email**:
   ```
   ai-collab-docs@your-project-id.iam.gserviceaccount.com
   ```
4. **Set permissions** to "Viewer" or "Commenter"
5. **Copy the sharing link**
6. **Paste the link** into AI Collab

### Example Service Account Email

Replace `your-project-id` with your actual Google Cloud project ID:
```
ai-collab-docs@ai-collab-123456.iam.gserviceaccount.com
```

## Security Notes

- The service account only has read access to documents
- Students must explicitly share documents with the service account
- No documents are stored permanently in AI Collab
- The service account cannot access any documents it hasn't been shared with

## Troubleshooting

### Common Issues

1. **"Document not found" error**
   - Make sure the document is shared with the service account
   - Check that the sharing link is correct

2. **"Service account not found" error**
   - Verify the service account key file is in the project root
   - Check that the file is named `service-account-key.json`

3. **"Permission denied" error**
   - Ensure the document is shared with the correct service account email
   - Check that the service account has at least "Viewer" permissions

### Testing

1. Create a test Google Doc
2. Share it with the service account
3. Try the "Analyze Doc" feature in AI Collab
4. Verify the document content is extracted and analyzed

## File Structure

```
AI_Collab/
├── service-account-key.json    # Google service account key
├── .env                        # Environment variables
├── google_docs.py             # Google Docs integration
└── ...
``` 