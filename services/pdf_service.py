# services/pdf_service.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
import io

def generate_certificate(attempt):
    """Generate PDF certificate for passing attempts"""
    
    # Create PDF in memory
    buffer = io.BytesIO()
    
    # Custom page size for certificate
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Colors
    primary_color = colors.HexColor("#1A5AFF")
    secondary_color = colors.HexColor("#2D3748")
    accent_color = colors.HexColor("#10B981")
    
    # ===== BACKGROUND =====
    c.setFillColor(colors.white)
    c.rect(0, 0, page_width, page_height, fill=1)
    
    # ===== SIMPLE BORDER =====
    c.setStrokeColor(colors.HexColor("#1A5AFF"))
    c.setLineWidth(2)
    c.rect(1*cm, 1*cm, page_width - 2*cm, page_height - 2*cm)
    
    # ===== HEADER =====
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(primary_color)
    c.drawCentredString(page_width/2, page_height - 3*cm, "IFIX ASSESSMENTS")
    
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(secondary_color)
    c.drawCentredString(page_width/2, page_height - 4*cm, "CERTIFICATE OF ACHIEVEMENT")
    
    c.setFont("Helvetica", 14)
    c.setFillColor(secondary_color)
    c.drawCentredString(page_width/2, page_height - 5*cm, "This certifies that")
    
    # ===== CANDIDATE NAME =====
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(secondary_color)
    name = attempt.user_name
    if len(name) > 25:
        c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(page_width/2, page_height - 7*cm, name)
    
    # ===== ASSESSMENT INFO =====
    c.setFont("Helvetica", 16)
    c.setFillColor(secondary_color)
    c.drawCentredString(page_width/2, page_height - 8.5*cm, "has successfully completed the")
    
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(primary_color)
    assessment_name = f"{attempt.assessment_type} Assessment"
    if len(assessment_name) > 40:
        c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width/2, page_height - 9.5*cm, assessment_name)
    
    # ===== FINAL SCORE =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(secondary_color)
    c.drawCentredString(page_width/2, page_height - 11.5*cm, "FINAL SCORE")
    
    c.setFont("Helvetica-Bold", 48)
    c.setFillColor(primary_color)
    c.drawCentredString(page_width/2, page_height - 13*cm, f"{attempt.percentage}%")
    
    # ===== SEPARATOR LINE =====
    line_y = page_height - 15*cm
    c.setStrokeColor(colors.HexColor("#E2E8F0"))
    c.setLineWidth(1)
    c.line(2*cm, line_y, page_width - 2*cm, line_y)
    
    # ===== DETAILS SECTION =====
    details_start_y = line_y - 1.5*cm
    
    # REMOVED ATTEMPT ID - using only 5 rows now
    data = [
        ["CANDIDATE", attempt.user_name],
        ["EMAIL", attempt.user_email],
        ["BUSINESS", attempt.user_business or "N/A"],
        ["ASSESSMENT", attempt.assessment_type],
        ["DATE", attempt.created_at.strftime("%B %d, %Y")],  # Auto date
        # ATTEMPT ID REMOVED
    ]
    
    row_height = 0.8*cm
    table_height = len(data) * row_height
    
    table = Table(data, colWidths=[3*cm, 11*cm], rowHeights=[row_height]*len(data))
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (0, -1), 12),
        ('FONTSIZE', (1, 0), (1, -1), 12),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), secondary_color),
        ('TEXTCOLOR', (1, 0), (1, -1), secondary_color),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    table.wrapOn(c, page_width, page_height)
    table.drawOn(c, page_width/2 - 7*cm, details_start_y - table_height)
    
    # ===== FOOTER =====
    footer_y = details_start_y - table_height - 2*cm
    
    # Issuer
    c.setFont("Helvetica", 12)
    c.setFillColor(secondary_color)
    c.drawCentredString(page_width/2, footer_y, "Issued by IFIX Assessments")
    
    # Certificate ID
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawCentredString(page_width/2, footer_y - 0.8*cm, f"Certificate ID: IFIX-3-20260130")
    
    # Verification text
    c.setFont("Helvetica", 9)
    c.drawCentredString(page_width/2, footer_y - 1.6*cm, 
                       "This certificate verifies successful completion of assessment requirements.")
    
    # Verification URL
    c.drawCentredString(page_width/2, footer_y - 2.4*cm, 
                       f"Verify at: https://businessworthysolutions.co.za/verify/3")
    
    # STATUS
    status_y = footer_y - 3.5*cm
    if attempt.percentage >= 70:
        c.setFillColor(colors.HexColor("#D1FAE5"))
        status_text = "STATUS: PASS"
        text_color = colors.HexColor("#065F46")
    else:
        c.setFillColor(colors.HexColor("#FEE2E2"))
        status_text = "STATUS: FAIL - NEEDS IMPROVEMENT"
        text_color = colors.HexColor("#991B1B")
    
    c.roundRect(page_width/2 - 3*cm, status_y - 0.6*cm, 
                6*cm, 1.2*cm, 10, fill=1)
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(text_color)
    c.drawCentredString(page_width/2, status_y - 0.3*cm, status_text)
    
    # Save PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

def save_certificate_to_file(attempt, folder="certificates"):
    """Generate and save certificate to file"""
    # Create folder if not exists
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Generate PDF
    pdf_buffer = generate_certificate(attempt)
    
    # Save to file
    filename = f"{folder}/certificate_{attempt.id}_{attempt.user_name.replace(' ', '_')}.pdf"
    with open(filename, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    return filename