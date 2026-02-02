import os
from dotenv import load_dotenv
load_dotenv()

import smtplib
from email.mime.text import MIMEText

def test_smtp():
    try:
        # Create message
        msg = MIMEText('Test email from IFIX Assessments')
        msg['Subject'] = 'IFIX Email Test'
        msg['From'] = os.getenv('MAIL_USERNAME')
        msg['To'] = 'nkosingiphilebhekithemba@gmail.com'  # Change to your test email
        
        # Connect to server
        server = smtplib.SMTP_SSL(
            os.getenv('MAIL_SERVER'), 
            int(os.getenv('MAIL_PORT'))
        )
        
        # Login
        server.login(
            os.getenv('MAIL_USERNAME'), 
            os.getenv('MAIL_PASSWORD')
        )
        
        # Send
        server.send_message(msg)
        server.quit()
        
        print("✅ Email test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

if __name__ == "__main__":
    test_smtp()