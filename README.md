# Job Application Tracker

A Streamlit application that automatically tracks your job applications by scanning your Gmail inbox. It extracts important information like company names, job titles, and application status, and presents them in an organized dashboard.

## Features

- 📧 Automatic email scanning for job applications
- 🏢 Company name extraction
- 💼 Job title detection
- 📊 Application status tracking
- 📅 Timeline view of applications
- 🔍 Search and filter capabilities

## Setup

1. Clone this repository:
```bash
git clone <your-repo-url>
cd Track
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google OAuth 2.0:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable the Gmail API
   - Create OAuth 2.0 credentials
   - Download the credentials and save as `credentials.json`

4. Create a `.env` file with your configuration:
```env
GMAIL_USER=your.email@gmail.com
```

5. Run the application:
```bash
streamlit run app.py
```

## Deployment

This application can be deployed on Streamlit Community Cloud:

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Deploy your app by selecting your repository
5. Add your environment variables in the Streamlit Cloud settings:
   - GMAIL_USER
   - Add any other sensitive information as secrets

## Security

- Never commit your `credentials.json` or `.env` file
- Store sensitive information as Streamlit secrets when deploying
- The app uses OAuth 2.0 for secure Gmail access

## Contributing

Feel free to open issues or submit pull requests for any improvements!

## License

MIT License
