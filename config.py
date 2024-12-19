import os
from dotenv import load_dotenv

load_dotenv()

# Gmail API credentials
GMAIL_CREDENTIALS_FILE = "credentials.json"

# Database configuration (SQLite)
DATABASE_URL = "sqlite:///job_applications.db"

# Email scanning configuration
SCAN_INTERVAL = 24  # hours
