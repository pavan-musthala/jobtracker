import streamlit as st
import pandas as pd
from database import DatabaseManager
from email_processor import EmailProcessor
from datetime import datetime
import plotly.express as px

def main():
    st.title("Job Application Tracker")
    
    try:
        # Initialize database
        db = DatabaseManager()
        
        # Sidebar for controls
        st.sidebar.title("Controls")
        if st.sidebar.button("Refresh Email Data"):
            try:
                with st.spinner("Scanning emails..."):
                    email_processor = EmailProcessor()
                    email_processor.scan_emails()
                st.success("Email scan complete!")
            except Exception as e:
                st.error(f"Error scanning emails: {str(e)}")
                return
        
        # Main content
        try:
            applications = db.get_all_applications()
            
            if applications:
                df = pd.DataFrame([
                    {
                        'Company': app.company,
                        'Job Title': app.job_title,
                        'Application Date': app.application_date,
                        'Status': app.status
                    }
                    for app in applications
                ])
                
                # Status distribution chart
                status_counts = df['Status'].value_counts()
                fig = px.pie(values=status_counts.values, 
                           names=status_counts.index, 
                           title='Application Status Distribution')
                st.plotly_chart(fig)
                
                # Applications table
                st.subheader("Your Applications")
                st.dataframe(df)
            else:
                st.info("No applications found. Click 'Refresh Email Data' to scan your inbox.")
                
        except Exception as e:
            st.error(f"Error loading applications: {str(e)}")
            
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")

if __name__ == "__main__":
    main()
