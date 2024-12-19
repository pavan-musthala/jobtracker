import streamlit as st
import pandas as pd
from email_processor import EmailProcessor
from database import DatabaseManager
import plotly.express as px
import config

st.set_page_config(page_title="Job Application Tracker", page_icon="💼", layout="wide")

def main():
    st.title("Job Application Tracker 💼")
    
    # Initialize database
    db = DatabaseManager()
    
    # Debug information
    st.sidebar.title("Debug Info")
    if st.sidebar.checkbox("Show Debug Info"):
        st.sidebar.write("Secrets available:", list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else "No secrets found")
        gmail_user = config.get_gmail_user()
        st.sidebar.write("Gmail User:", gmail_user if gmail_user else "Not configured")
    
    # Check if credentials are properly configured
    try:
        gmail_user = config.get_gmail_user()
        if not gmail_user:
            st.error("""
            Gmail user not configured. Please set GMAIL_USER in Streamlit secrets.
            
            Your secrets should look like this:
            ```toml
            [google_credentials]
            client_id = "..."
            ...
            
            GMAIL_USER = "your.email@gmail.com"
            ```
            Make sure GMAIL_USER is outside the [google_credentials] section.
            """)
            return
            
        # Create email processor
        email_processor = EmailProcessor()
        
        # Add refresh button
        if st.button("🔄 Refresh Email Data"):
            with st.spinner("Scanning emails..."):
                try:
                    email_processor.scan_emails()
                    st.success("Email scan complete!")
                except Exception as e:
                    st.error(f"Error scanning emails: {str(e)}")
                    st.error("Please check your Google Cloud Console configuration and make sure:")
                    st.markdown("""
                    1. Gmail API is enabled
                    2. OAuth consent screen is configured
                    3. OAuth credentials are properly set up
                    4. Redirect URIs include `http://localhost`
                    """)
        
        # Display applications
        applications = db.get_all_applications()
        if applications:
            df = pd.DataFrame(applications)
            
            # Convert date strings to datetime
            df['application_date'] = pd.to_datetime(df['application_date'])
            
            # Status distribution
            st.subheader("Application Status Distribution 📊")
            status_counts = df['status'].value_counts()
            fig = px.pie(values=status_counts.values, 
                        names=status_counts.index, 
                        title="Application Status Distribution")
            st.plotly_chart(fig)
            
            # Applications over time
            st.subheader("Applications Over Time 📈")
            daily_apps = df.resample('D', on='application_date').size()
            fig = px.line(x=daily_apps.index, y=daily_apps.values,
                         title="Daily Applications",
                         labels={'x': 'Date', 'y': 'Number of Applications'})
            st.plotly_chart(fig)
            
            # Applications table
            st.subheader("All Applications 📋")
            
            # Status filter
            status_filter = st.multiselect(
                "Filter by Status",
                options=df['status'].unique(),
                default=df['status'].unique()
            )
            
            # Apply filters
            filtered_df = df[df['status'].isin(status_filter)]
            
            # Display table
            st.dataframe(
                filtered_df[['company_name', 'position', 'application_date', 'status']]
                .sort_values('application_date', ascending=False)
                .reset_index(drop=True),
                use_container_width=True
            )
            
        else:
            st.info("No applications found. Click 'Refresh Email Data' to scan your inbox.")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.error("Please make sure you have configured your credentials correctly in Streamlit secrets.")
        st.info("Check the debug information in the sidebar for more details.")

if __name__ == "__main__":
    main()
