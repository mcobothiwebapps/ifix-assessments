import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

print("=== WORKING SETTINGS FROM test_email_simple.py ===")
print(f"Server: {os.getenv('MAIL_SERVER')}")
print(f"Port: {os.getenv('MAIL_PORT')}")
print(f"Username: {os.getenv('MAIL_USERNAME')}")

# Test which combination works
msg = EmailMessage()
msg['Subject'] = 'Test'
msg['From'] = os.getenv('MAIL_USERNAME')
msg['To'] = 'your_email@gmail.com'
msg.set_content('Test')

# Try SSL
try:
    with smtplib.SMTP_SSL(os.getenv('MAIL_SERVER'), int(os.getenv('MAIL_PORT'))) as server:
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        server.send_message(msg)
    print("✅ SSL connection works")
except Exception as e:
    print(f"❌ SSL failed: {e}")

# Try TLS
try:
    with smtplib.SMTP(os.getenv('MAIL_SERVER'), int(os.getenv('MAIL_PORT'))) as server:
        server.starttls()
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        server.send_message(msg)
    print("✅ TLS connection works")
except Exception as e:
    print(f"❌ TLS failed: {e}")