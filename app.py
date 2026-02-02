import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from flask import Flask
from database import init_database

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "ifix_assessments_temp_key_123"

# Email configuration with defaults
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')

print("✅ Email service ready (using direct SMTP)")

# Initialize database
init_database(app)

# IMPORTANT: Import blueprints AFTER creating app
from routes.main import main
from routes.admin import admin

app.register_blueprint(main)
app.register_blueprint(admin)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)