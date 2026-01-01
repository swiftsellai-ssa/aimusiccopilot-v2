# backend/create_analytics_tables.py
"""
Create analytics tables in the database
Run this once to add analytics tables to existing database
"""

from database import engine
from models.analytics import Base as AnalyticsBase

# Create only analytics tables
print("Creating analytics tables...")
AnalyticsBase.metadata.create_all(bind=engine)
print("✅ Analytics tables created successfully!")
print("Tables created: generation_events, user_sessions, analytics_summary")
