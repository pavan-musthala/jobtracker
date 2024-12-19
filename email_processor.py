from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from database import DatabaseManager
from bs4 import BeautifulSoup
import re
from datetime import datetime
import base64
import email.utils
import time
import config

class EmailProcessor:
    def __init__(self):
        """Initialize the EmailProcessor"""
        self.service = None
        self.setup_gmail_service()

    def setup_gmail_service(self):
        """Set up Gmail API service"""
        creds = None
        token_path = config.TOKEN_PATH
        credentials_path = config.get_gmail_credentials()

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, config.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

        # Clean up temporary credentials file if it exists
        if credentials_path == "temp_credentials.json" and os.path.exists(credentials_path):
            os.remove(credentials_path)

    def extract_date_from_email(self, headers):
        """Extract the actual date from email headers"""
        for header in headers:
            if header['name'].lower() == 'date':
                # Parse email date format to datetime
                date_tuple = email.utils.parsedate_tz(header['value'])
                if date_tuple:
                    # Convert to timestamp and then to datetime
                    timestamp = email.utils.mktime_tz(date_tuple)
                    return datetime.fromtimestamp(timestamp).date()
        return datetime.now().date()

    def clean_text(self, text):
        """Clean email text by removing footers and formatting"""
        # Remove common email footers and disclaimers
        footers = [
            "this email and any attachments",
            "this message contains confidential information",
            "if you received this email in error",
            "if you are not the intended recipient",
            "this email is confidential",
            "any views or opinions",
            "this communication is for",
            "please do not reply to this email",
            "please consider the environment",
            "please note that",
        ]
        
        # Clean the text
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces
        text = text.replace('\n', ' ').replace('\r', ' ')  # Replace newlines
        text = re.sub(r'<[^>]+>', ' ', text)  # Remove HTML tags
        
        # Remove footers
        text_lower = text.lower()
        for footer in footers:
            idx = text_lower.find(footer)
            if idx != -1:
                text = text[:idx]
        
        return text.strip()

    def clean_company_name(self, name):
        """Clean and validate company name"""
        if not name:
            return None
            
        # Remove unwanted prefixes/suffixes
        name = re.sub(r'(?i)\s*(?:inc|ltd|limited|corp|corporation|llc|llp|pvt|private|technologies|technology|solutions|consulting)\.?\s*$', '', name)
        name = re.sub(r'["\']', '', name)  # Remove quotes
        name = ' '.join(name.split())  # Clean whitespace
        
        # Skip if it looks like a personal name (contains multiple words and each word is capitalized)
        words = name.split()
        if len(words) > 1 and all(word[0].isupper() for word in words if len(word) > 1):
            return None
        
        # Skip common invalid names
        invalid_names = {
            'the', 'this', 'your', 'job', 'application', 'position', 'role', 
            'careers', 'jobs', 'recruitment', 'talent', 'hr', 'hire', 'team',
            'reply', 'noreply', 'no-reply', 'donotreply', 'do-not-reply',
            'notifications', 'alert', 'update', 'message', 'mail', 'email'
        }
        if name.lower() in invalid_names:
            return None
            
        # Skip if too short or just numbers
        if len(name) <= 2 or name.replace(' ', '').isdigit():
            return None
            
        return name.strip()

    def extract_company_name(self, text, subject, email_from):
        """Extract company name from email content"""
        # First try to get company name from email sender
        if email_from:
            # Try display name first (e.g., "Company Name" <email@domain.com>)
            display_match = re.match(r'^"?([^"@<>]+)"?\s*(?:<[^>]+>)?$', email_from)
            if display_match:
                company = self.clean_company_name(display_match.group(1))
                if company:
                    return company

            # Try domain name (but skip common email providers)
            domain_match = re.search(r'@([\w-]+)\.([\w.]+)', email_from)
            if domain_match:
                domain = domain_match.group(1)
                if domain.lower() not in ['gmail', 'yahoo', 'hotmail', 'outlook', 'aol', 'proton', 'icloud', 'mail', 'email']:
                    company = self.clean_company_name(domain)
                    if company:
                        return company.title()

        # Common patterns to find company name
        patterns = [
            # Direct mentions
            r"(?i)welcome to ([\w\s&-]+?)(?:['s]| team|\s*$|\.)",
            r"(?i)joining ([\w\s&-]+?)(?:['s]| team|\s*$|\.)",
            r"(?i)applying to ([\w\s&-]+?)(?:['s]| team|\s*$|\.)",
            r"(?i)application (?:at|with|to) ([\w\s&-]+?)(?:['s]| team|\s*$|\.)",
            r"(?i)position at ([\w\s&-]+?)(?:['s]| team|\s*$|\.)",
            r"(?i)career(?:s)? at ([\w\s&-]+?)(?:['s]| team|\s*$|\.)",
            r"(?i)from ([\w\s&-]+?)(?:['s]| team| careers| recruitment| hiring|\s*$|\.)",
            r"(?i)on behalf of ([\w\s&-]+?)(?:['s]| team|\s*$|\.)",
        ]

        # Check subject first, then body
        for text_to_check in [subject, text]:
            for pattern in patterns:
                match = re.search(pattern, text_to_check)
                if match:
                    company = self.clean_company_name(match.group(1))
                    if company:
                        return company

        return "Unknown Company"

    def clean_job_title(self, title):
        """Clean and validate job title"""
        if not title:
            return None
        
        # Remove unwanted words and clean up
        title = re.sub(r'(?i)^(?:the|a|an)\s+', '', title)
        title = re.sub(r'(?i)\s+(?:role|position|job|vacancy|opening)$', '', title)
        title = re.sub(r'(?i)^(?:position|role|job|vacancy|opening)\s+(?:of|as)\s+', '', title)
        title = ' '.join(title.split())  # Clean whitespace
        
        # Remove if it's just generic words
        invalid_titles = {
            'job', 'role', 'position', 'vacancy', 'opening', 'the', 'this', 
            'opportunity', 'application', 'your', 'our', 'career', 'employment'
        }
        if title.lower() in invalid_titles:
            return None
        
        # Remove if it's a partial sentence (contains certain verbs or prepositions)
        sentence_indicators = {
            'will be', 'have been', 'has been', 'we are', 'you are', 'and will',
            'please', 'thank you', 'regards', 'sincerely', 'dear', 'hello', 'hi'
        }
        if any(indicator in title.lower() for indicator in sentence_indicators):
            return None
        
        # Remove very short titles or ones that look like sentences
        if len(title) <= 2 or len(title.split()) > 8:  
            return None
            
        return title.strip()

    def extract_job_title(self, text, subject):
        """Extract job title from email content"""
        # Try to find job title in subject first
        subject_patterns = [
            # Look for common job title patterns in subject
            r"(?i)(?:^|\s)((?:junior\s+|senior\s+|lead\s+|principal\s+|staff\s+)?(?:software|data|ml|ai|frontend|backend|fullstack|full\s*stack|web|mobile|cloud|devops|site|reliability|security|systems|network|database|analytics|business|marketing|sales|product|project|program|quality|test|support|customer|technical|it|information|technology|research|development|engineering|operations|infrastructure|platform|solutions|services|analyst|engineer|developer|scientist|architect|manager|consultant|specialist|administrator|coordinator|designer|director|lead|head)\s*(?:analyst|engineer|developer|scientist|architect|manager|consultant|specialist|administrator|coordinator|designer|director|lead|head)?)[^\n\.,]*",
            
            # Extract anything in parentheses that looks like a job title
            r"(?i)[/\(]([^/\(\)]*(?:analyst|engineer|developer|scientist|architect|manager|consultant|specialist|administrator|coordinator|designer|director|lead|head)[^/\(\)]*)[/\)]",
            
            # Look for job titles at the start or end of subject
            r"(?i)^([^-\n]*(?:analyst|engineer|developer|scientist|architect|manager|consultant|specialist|administrator|coordinator|designer|director|lead|head)[^-\n]*?)(?:\s*[-–]\s*|$)",
            r"(?i)(?:^|\s*[-–]\s*)([^-\n]*(?:analyst|engineer|developer|scientist|architect|manager|consultant|specialist|administrator|coordinator|designer|director|lead|head)[^-\n]*?)$",
        ]
        
        # First try to extract from subject
        for pattern in subject_patterns:
            match = re.search(pattern, subject)
            if match:
                title = self.clean_job_title(match.group(1))
                if title:
                    return title

        # Common patterns to find job title in email body
        body_patterns = [
            # Thank you patterns
            r"(?i)thank you for (?:applying|your application|your interest) (?:for|to) (?:the )?(?:position of |role of |job as )?[\"']?([\w\s-]+?)[\"']?(?=\s+(?:at|with|in|position|role|job|$|\.|,))",
            r"(?i)thank you for taking the time to apply for (?:the )?(?:position of |role of |job as )?[\"']?([\w\s-]+?)[\"']?(?=\s+(?:at|with|in|position|role|job|$|\.|,))",
            
            # Application patterns
            r"(?i)(?:regarding|about|received) your application for (?:the )?(?:position of |role of |job as )?[\"']?([\w\s-]+?)[\"']?(?=\s+(?:at|with|in|position|role|job|$|\.|,))",
            r"(?i)applied for (?:the )?(?:position of |role of |job as )?[\"']?([\w\s-]+?)[\"']?(?=\s+(?:at|with|in|position|role|job|$|\.|,))",
            
            # Direct mention patterns
            r"(?i)position:\s*[\"']?([\w\s-]+?)[\"']?(?=\s|$|\.|,)",
            r"(?i)role:\s*[\"']?([\w\s-]+?)[\"']?(?=\s|$|\.|,)",
            r"(?i)job title:\s*[\"']?([\w\s-]+?)[\"']?(?=\s|$|\.|,)",
            r"(?i)vacancy:\s*[\"']?([\w\s-]+?)[\"']?(?=\s|$|\.|,)",
            
            # Broader patterns
            r"(?i)(?:for|as) (?:a|an|the)?\s*[\"']?([\w\s-]+?)[\"']?\s+(?:position|role|job|opportunity)",
            r"(?i)(?:for|as) (?:a|an|the)?\s*[\"']?([\w\s-]+?)[\"']?\s+(?:at|with)",
        ]

        # Try to find in email body
        for pattern in body_patterns:
            match = re.search(pattern, text)
            if match:
                title = self.clean_job_title(match.group(1))
                if title:
                    return title

        # If still no match, try to extract from subject using more general patterns
        general_patterns = [
            # Look for anything that might be a job title
            r"(?i)(?:^|\s)((?:junior|senior|lead|principal|staff)\s+[\w\s-]+)(?:\s|$)",
            r"(?i)(?:^|\s)([\w\s-]+?\s+(?:analyst|engineer|developer|scientist|architect|manager|consultant|specialist|administrator|coordinator|designer|director|lead|head))(?:\s|$)",
        ]
        
        for pattern in general_patterns:
            match = re.search(pattern, subject)
            if match:
                title = self.clean_job_title(match.group(1))
                if title:
                    return title

        return "Unknown Position"

    def extract_application_info(self, email_body, subject="", email_from="", headers=None):
        try:
            # Get the actual email date
            email_date = self.extract_date_from_email(headers) if headers else datetime.now().date()
            
            # Decode and clean email body
            if email_body:
                try:
                    email_body = base64.urlsafe_b64decode(email_body.encode('ASCII')).decode('utf-8')
                except Exception as e:
                    print(f"Error decoding email body: {e}")
                    email_body = ""
            
            # Clean and extract text
            soup = BeautifulSoup(email_body, 'html.parser')
            text = self.clean_text(soup.get_text())
            
            # Extract information
            company = self.extract_company_name(text, subject, email_from)
            job_title = self.extract_job_title(text, subject)
            status = self.determine_status(text, subject)
            
            return {
                'company': company,
                'job_title': job_title,
                'status': status,
                'application_date': email_date
            }
        except Exception as e:
            print(f"Error extracting application info: {e}")
            return {
                'company': "Unknown Company",
                'job_title': "Unknown Position",
                'status': "Under Review",
                'application_date': datetime.now().date()
            }
    
    def scan_emails(self):
        try:
            # Search for relevant emails from the last month
            query = """
                subject:(
                    application OR applied OR interview OR 
                    job OR position OR role OR career OR 
                    offer OR "thank you" OR recruitment OR
                    "thank you for applying"
                ) 
                newer_than:30d
            """
            
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            if not messages:
                print("No new job-related emails found")
                return
            
            for message in messages:
                try:
                    msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                    email_data = msg['payload']
                    
                    # Get headers
                    headers = email_data['headers']
                    
                    # Get subject and sender
                    subject = ""
                    email_from = ""
                    for header in headers:
                        if header['name'].lower() == 'subject':
                            subject = header['value']
                        elif header['name'].lower() == 'from':
                            email_from = header['value']
                    
                    # Extract email body
                    email_body = ""
                    if 'parts' in email_data:
                        for part in email_data['parts']:
                            if part['mimeType'] == 'text/plain':
                                email_body = part['body'].get('data', '')
                                break
                    else:
                        email_body = email_data['body'].get('data', '')
                    
                    # Extract application info
                    info = self.extract_application_info(email_body, subject, email_from, headers)
                    
                    # Only add if we have meaningful information
                    if info['company'] != "Unknown Company" or info['job_title'] != "Unknown Position":
                        self.db.add_application(
                            company=info['company'],
                            job_title=info['job_title'],
                            application_date=info['application_date'],
                            status=info['status']
                        )
                        
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scanning emails: {e}")
            raise

    def determine_status(self, text, subject):
        """Determine application status from email content"""
        text = text.lower()
        subject = subject.lower()
        full_text = f"{subject} {text}"
        
        # Strong rejection indicators (if any of these are found, it's definitely a rejection)
        strong_rejection_phrases = [
            "regret to inform",
            "we regret",
            "regrettably",
            "regret to advise",
            "regret to say",
            "regret to tell",
            "regret to communicate",
        ]
        
        # Check for strong rejection indicators first
        if any(phrase in full_text for phrase in strong_rejection_phrases):
            return "Rejected"
        
        # Other rejection indicators (check these only if no strong indicators found)
        rejection_phrases = [
            "unfortunately",
            "not moving forward",
            "decided to proceed with other",
            "not selected",
            "not successful",
            "not shortlisted",
            "not proceed",
            "position has been filled",
            "selected another candidate",
            "pursue other candidates",
            "better suited candidates",
            "do not match our current requirements",
            "unable to offer",
            "cannot take your application forward",
            "wish you success in your future",
            "best of luck in your future",
            "thank you for your interest",  # When combined with above phrases
            "keep your profile on file",    # When combined with above phrases
        ]
        
        # Interview indicators
        interview_phrases = [
            "interview",
            "would like to meet",
            "schedule a call",
            "discuss your application",
            "next steps",
            "move forward with your application",
            "pleased to inform",
            "successful in your application",
            "move to the next stage",
            "would like to speak with you",
            "invite you to",
            "follow up discussion",
        ]
        
        # Offer indicators
        offer_phrases = [
            "job offer",
            "offer letter",
            "pleased to offer",
            "formal offer",
            "offer of employment",
            "would like to offer",
            "happy to offer",
        ]
        
        # Application received indicators
        received_phrases = [
            "application received",
            "thank you for applying",
            "received your application",
            "confirm receipt",
            "successfully submitted",
            "application has been submitted",
            "thank you for your interest",  # Only if no rejection phrases
            "will review your application",
            "application is under review",
        ]
        
        # Check for other statuses
        if any(phrase in full_text for phrase in offer_phrases):
            return "Offer Received"
        elif any(phrase in full_text for phrase in rejection_phrases):
            return "Rejected"
        elif any(phrase in full_text for phrase in interview_phrases):
            return "Interview Scheduled"
        elif any(phrase in full_text for phrase in received_phrases):
            return "Application Received"
            
        return "Under Review"
