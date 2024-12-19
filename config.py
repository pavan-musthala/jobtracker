import os
import json
import streamlit as st
from pathlib import Path

def get_gmail_user():
    """Get Gmail user from Streamlit secrets"""
    # Debug print
    st.write("Debug - All secrets:", st.secrets)
    
    try:
        # Try direct dictionary access
        secrets_dict = dict(st.secrets)
        if 'GMAIL_USER' in secrets_dict:
            return secrets_dict['GMAIL_USER']
        
        st.error("GMAIL_USER not found in secrets. Available keys: " + ", ".join(secrets_dict.keys()))
        return None
    except Exception as e:
        st.error(f"Error accessing secrets: {str(e)}")
        return None

def get_gmail_credentials():
    """Get Gmail API credentials from Streamlit secrets or local file"""
    try:
        # Try to get credentials from Streamlit secrets
        secrets_dict = dict(st.secrets)
        if 'google_credentials' in secrets_dict:
            creds = secrets_dict['google_credentials']
            credentials = {
                "installed": {
                    "client_id": creds['client_id'],
                    "project_id": creds['project_id'],
                    "auth_uri": creds['auth_uri'],
                    "token_uri": creds['token_uri'],
                    "auth_provider_x509_cert_url": creds['auth_provider_x509_cert_url'],
                    "client_secret": creds['client_secret'],
                    "redirect_uris": creds['redirect_uris']
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
                    "credentials.json not found and google_credentials not in secrets"
                )
            return creds_path
    except Exception as e:
        st.error(f"Error loading credentials: {str(e)}")
        raise

# Token file path
TOKEN_PATH = "token.pickle"

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Email search query
SEARCH_QUERY = 'subject:"applied" OR subject:"application" OR subject:"thank you for applying" OR subject:"interview" OR subject:"position" OR subject:"job" OR subject:"opportunity" OR subject:"candidacy" OR subject:"candidate" OR subject:"recruitment" OR subject:"hiring" OR subject:"consideration"'

# Database configuration
DATABASE_URL = "sqlite:///job_applications.db"

# Email scanning configuration
SCAN_INTERVAL = 24  # hours
