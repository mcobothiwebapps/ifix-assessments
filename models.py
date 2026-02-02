from datetime import datetime
import json  # Make sure this import is here
from database import db

class AssessmentAttempt(db.Model):
    __tablename__ = 'assessment_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    user_business = db.Column(db.String(100))
    user_phone = db.Column(db.String(20))
    assessment_type = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    answers = db.Column(db.Text)  # JSON string of answers
    
    # TIMESTAMP FIELDS
    started_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<AssessmentAttempt {self.id} - {self.user_email}>'
    
    @property
    def time_taken(self):
        """Calculate actual time taken for the assessment"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def time_taken_minutes(self):
        """Get time taken in minutes"""
        time_taken = self.time_taken
        if time_taken:
            return int(time_taken.total_seconds() / 60)
        return None
    
    @property
    def time_taken_seconds(self):
        """Get remaining seconds"""
        time_taken = self.time_taken
        if time_taken:
            return int(time_taken.total_seconds() % 60)
        return None
    
    @property
    def time_taken_formatted(self):
        """Format time as X minutes Y seconds"""
        minutes = self.time_taken_minutes
        seconds = self.time_taken_seconds
        
        if minutes is not None and seconds is not None:
            if seconds == 0:
                return f"{minutes} minutes"
            else:
                return f"{minutes} minutes {seconds} seconds"
        return "Time not recorded"
    
    @property
    def parsed_answers(self):
        """Parse JSON answers into Python dict/list"""
        if self.answers:
            try:
                return json.loads(self.answers)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    @property
    def passed(self):
        """Check if user passed (70% or higher)"""
        return self.percentage >= 70