# Job Application Tracker

A sophisticated Python-based application that automatically tracks and manages your job applications by intelligently scanning your Gmail inbox. Built with Streamlit and the Gmail API, this tool eliminates the need for manual tracking and provides real-time insights into your job application process.

## 🌟 Key Features

### 📧 Automated Email Processing
- Automatically scans your Gmail inbox for job-related emails
- Intelligently identifies application confirmations, rejections, and interview invitations
- Extracts key information using advanced pattern matching and NLP techniques

### 🎯 Smart Information Extraction
- **Company Names**: Accurately extracts company names from email senders and content
- **Job Titles**: Identifies job positions using sophisticated pattern matching
- **Application Status**: Automatically categorizes emails into:
  - Application Received
  - Under Review
  - Interview Scheduled
  - Rejected
  - Offer Received

### 📊 Interactive Dashboard
- Clean, modern interface built with Streamlit
- Real-time status updates of all applications
- Sortable and filterable application list
- Visual analytics and insights

### 🔒 Security & Privacy
- Secure Gmail integration using OAuth 2.0
- No email passwords stored
- Local database storage for application data
- Environment variables for sensitive information

## 🛠️ Technical Architecture

### Core Components
1. **Email Processing Engine**
   - Gmail API integration
   - Advanced regex pattern matching
   - Intelligent text parsing
   - BeautifulSoup for HTML parsing

2. **Data Management**
   - SQLite database for local storage
   - Efficient data models
   - Automated data updates

3. **User Interface**
   - Streamlit-based dashboard
   - Interactive data visualization
   - Real-time updates

### Technologies Used
- **Python**: Core programming language
- **Streamlit**: Web interface and dashboard
- **Gmail API**: Email access and processing
- **SQLite**: Data storage
- **BeautifulSoup4**: HTML parsing
- **Regular Expressions**: Pattern matching
- **Pandas**: Data manipulation
- **OAuth2**: Security and authentication

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Gmail account
- Google Cloud Platform account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/pavan-musthala/jobtracker.git
cd jobtracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google OAuth 2.0:
   - Create a project in Google Cloud Console
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials as `credentials.json`

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run the application:
```bash
streamlit run app.py
```

## 💡 Usage

1. **First-time Setup**
   - Launch the application
   - Click "Authorize Gmail" button
   - Complete Google OAuth authentication
   - Grant necessary permissions

2. **Dashboard Navigation**
   - View all applications in the main table
   - Use filters to sort by company, status, or date
   - Click "Refresh Email Data" to scan for new applications

3. **Application Management**
   - Automatically tracks new applications
   - Updates status based on email communications
   - Provides insights into application progress

## 🔄 Continuous Improvement

The application uses machine learning techniques to continuously improve:
- Pattern recognition for job titles
- Company name extraction
- Status classification
- Email relevance detection

## 🤝 Contributing

Contributions are welcome! Here's how you can help:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Gmail API Documentation
- Streamlit Community
- Python Regex Documentation
- Beautiful Soup Documentation

## 📞 Support

For support, email [your-email] or open an issue on GitHub.
