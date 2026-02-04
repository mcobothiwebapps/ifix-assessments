from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_database(app):
    """Initialize database with Flask app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assessments.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database initialized and tables created")