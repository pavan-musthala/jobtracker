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
    
    # Check if credentials are properly configured
    try:
        gmail_user = config.get_gmail_user()
        if not gmail_user:
            st.error("Gmail user not configured. Please set GMAIL_USER in Streamlit secrets or environment variables.")
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
        st.info("Please make sure you have configured your credentials correctly in Streamlit secrets.")

if __name__ == "__main__":
    main()
