import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Gmail API credentials
def get_gmail_credentials():
    """Get Gmail API credentials from Streamlit secrets or local file"""
    try:
        # Try to get credentials from Streamlit secrets
        if 'google_credentials' in st.secrets:
            credentials = {
                "installed": {
                    "client_id": st.secrets.google_credentials.client_id,
                    "project_id": st.secrets.google_credentials.project_id,
                    "auth_uri": st.secrets.google_credentials.auth_uri,
                    "token_uri": st.secrets.google_credentials.token_uri,
                    "auth_provider_x509_cert_url": st.secrets.google_credentials.auth_provider_x509_cert_url,
                    "client_secret": st.secrets.google_credentials.client_secret,
                    "redirect_uris": st.secrets.google_credentials.redirect_uris
                }
            }
            # Write credentials to a temporary file
            creds_path = "temp_credentials.json"
            with open(creds_path, "w") as f:
                json.dump(credentials, f)
            return creds_path
        else:
            # Fallback to local credentials.json
            creds_path = "credentials.json"
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    "credentials.json not found. Please either add it locally or configure Streamlit secrets."
                )
            return creds_path
    except Exception as e:
        st.error(f"Error loading credentials: {str(e)}")
        raise

def get_gmail_user():
    """Get Gmail user from environment or Streamlit secrets"""
    # Try to get from Streamlit secrets first
    if 'GMAIL_USER' in st.secrets:
        return st.secrets.GMAIL_USER
    
    # Fallback to environment variable
    return os.getenv('GMAIL_USER')

# Token file path
TOKEN_PATH = "token.pickle"

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Email search query
SEARCH_QUERY = 'subject:"applied" OR subject:"application" OR subject:"thank you for applying" OR subject:"interview" OR subject:"position" OR subject:"job" OR subject:"opportunity" OR subject:"candidacy" OR subject:"candidate" OR subject:"recruitment" OR subject:"hiring" OR subject:"consideration"'

# Database configuration (SQLite)
DATABASE_URL = "sqlite:///job_applications.db"

# Email scanning configuration
SCAN_INTERVAL = 24  # hours
