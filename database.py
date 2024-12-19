from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from config import DATABASE_URL

Base = declarative_base()

class Application(Base):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    company = Column(String(255))
    job_title = Column(String(255))
    application_date = Column(Date)
    status = Column(String(50))

class DatabaseManager:
    def __init__(self):
        try:
            self.engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    def add_application(self, company, job_title, application_date, status):
        try:
            application = Application(
                company=company,
                job_title=job_title,
                application_date=application_date,
                status=status
            )
            self.session.add(application)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error adding application: {e}")
            raise
    
    def get_all_applications(self):
        try:
            return self.session.query(Application).all()
        except Exception as e:
            print(f"Error retrieving applications: {e}")
            return []
            
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
