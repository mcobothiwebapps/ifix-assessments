import os
from flask import current_app, render_template_string
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_assessment_results(attempt, user_email):
    """Send assessment results email with certificate"""
    
    subject = f"IFIX Assessment Results - {attempt.assessment_type}"
    
    # Check if passed (70% or higher)
    passed = attempt.percentage >= 70
    
    # EXTREMELY SIMPLIFIED EMAIL - NO COMPLEX HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #1A5AFF; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .certificate {{ background: white; padding: 30px; border: 2px solid #1A5AFF; border-radius: 0 0 10px 10px; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; text-align: center; font-size: 12px; }}
            .status-pass {{ background: #d1fae5 !important; color: #065f46 !important; }}
            .status-fail {{ background: #fee2e2 !important; color: #991b1b !important; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
             <img src="cid:ifix_logo" alt="IFIX Assessments" style="height: 60px; margin-bottom: 20px;">
                <h2>IFIX Assessment Results</h2>
                <p>Your {attempt.assessment_type} assessment has been graded</p>
            </div>
            
            <!-- Show certificate only if passed (70% or higher) -->
            {"<div class='certificate'>" if passed else "<div style='background: white; padding: 30px; border-radius: 0 0 10px 10px;'>"}
                
                {"<div style='text-align: center; margin-bottom: 30px;'>" if passed else "<div style='text-align: center; margin-bottom: 30px; color: #666;'>"}
                    <h3 style='color: #1A5AFF; margin: 0;'>IFIX ASSESSMENTS</h3>
                    <h4 style='color: #333; margin: 10px 0;'>CERTIFICATE OF ACHIEVEMENT</h4>
                    <p>This certifies that</p>
                    <h2 style='color: #1A5AFF; margin: 20px 0; padding: 10px 0; border-top: 2px solid #1A5AFF; border-bottom: 2px solid #1A5AFF;'>
                        {attempt.user_name}
                    </h2>
                    <p>has successfully completed the</p>
                    <h3 style='color: #333; margin: 15px 0;'>{attempt.assessment_type} Assessment</h3>
                    
                    <div style='margin: 30px 0;'>
                        <p style='color: #666; margin: 0;'>FINAL SCORE</p>
                        <h1 style='color: #1A5AFF; font-size: 48px; margin: 10px 0;'>{attempt.percentage}%</h1>
                    </div>
                </div>
                
                <div style='background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;'>
                    <p><strong>CANDIDATE:</strong> {attempt.user_name}</p>
                    <p><strong>EMAIL:</strong> {attempt.user_email}</p>
                    <p><strong>BUSINESS:</strong> {attempt.user_business or "N/A"}</p>
                    <p><strong>ASSESSMENT:</strong> {attempt.assessment_type}</p>
                    <p><strong>DATE:</strong> {attempt.created_at.strftime('%B %d, %Y')}</p>
                </div>
                
                <div style='text-align: center; margin-top: 30px;'>
                    {"<p><strong>Issued by IFIX Assessments</strong></p>" if passed else ""}
                    
                    {"<p>Certificate ID: IFIX-3-20260130</p>" if passed else ""}
                    
                    {"<p>This certificate verifies successful completion of assessment requirements.</p>" if passed else ""}
                    
                    {"<p><a href='https://businessworthysolutions.co.za/verify/3'>Verify at: https://businessworthysolutions.co.za/verify/3</a></p>" if passed else ""}
                    
                    <!-- FIXED: Inline styles for status badge -->
                    <div style='padding: 10px 20px; border-radius: 20px; display: inline-block; margin-top: 20px; font-weight: bold; background: {"#d1fae5" if passed else "#fee2e2"}; color: {"#065f46" if passed else "#991b1b"};'>
                        STATUS: {"PASS" if passed else "FAIL - NEEDS IMPROVEMENT"}
                    </div>
                    
                    {"<p style='margin-top: 20px; color: #666;'><em>Note: A PDF certificate is available for download from the assessment portal.</em></p>" if passed else ""}
                    
                    {f"<p style='margin-top: 20px; color: #991b1b;'><strong>Note:</strong> You scored {attempt.percentage}%. You need 70% or higher to pass and receive a certificate. Please try again.</p>" if not passed else ""}
                </div>
            </div>
            
            <div class="footer">
                <p>© {attempt.created_at.strftime('%Y')} IFIX Assessments Platform</p>
                <p>BusinessWorthy Solutions | Professional Assessment System</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    
    # ===== DEBUG: Check if email is being called =====
    print(f"\n📧 DEBUG: Starting email send function")
    print(f"   To: {user_email}")
    print(f"   Subject: {subject}")
    print(f"   From: {os.getenv('MAIL_USERNAME')}")
    print(f"   SMTP: {os.getenv('MAIL_SERVER')}:{os.getenv('MAIL_PORT')}")
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
        msg['To'] = user_email
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # TRY WITHOUT LOGO FIRST to simplify
        print("   Note: Skipping logo attachment for testing")
        
        # Send email
        print(f"   Connecting to SMTP server...")
        with smtplib.SMTP_SSL(
            os.getenv('MAIL_SERVER'), 
            int(os.getenv('MAIL_PORT'))
        ) as server:
            print(f"   Connected to {os.getenv('MAIL_SERVER')}")
            print(f"   Logging in...")
            server.login(
                os.getenv('MAIL_USERNAME'), 
                os.getenv('MAIL_PASSWORD')
            )
            print(f"   Login successful")
            print(f"   Sending email...")
            server.send_message(msg)
            print(f"   Email sent successfully!")
        
        print(f"✅ EMAIL SENT SUCCESSFULLY to {user_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP AUTHENTICATION ERROR: Check username/password")
        print(f"   Error: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False