# routes/admin.py - FIXED VERSION
from flask import Blueprint, render_template, jsonify, make_response
import json
import csv
from io import StringIO
from datetime import datetime
import os
from database import db
from models import AssessmentAttempt

admin = Blueprint("admin", __name__, url_prefix="/admin")

# Define load_questions locally to avoid circular imports
def load_questions(assessment_type):
    """Load questions from JSON file based on assessment type"""
    try:
        # Determine which JSON file to load
        if assessment_type == "Municipalities":
            file_path = os.path.join("data", "questions.json")
        else:
            file_path = os.path.join("data", "questions_non_municipalities.json")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"⚠️ Warning: Questions file not found: {file_path}")
            return []
        
        # Load questions from JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        print(f"✅ Loaded {len(questions)} questions for {assessment_type}")
        return questions
        
    except Exception as e:
        print(f"❌ Error loading questions: {e}")
        return []

# Temporary admin password (we'll implement proper auth later)
ADMIN_PASSWORD = "ifixadmin123"

@admin.route("/")
def dashboard():
    """Admin dashboard showing all attempts"""
    # JUST query the attempts - properties are calculated automatically by the model
    attempts = AssessmentAttempt.query.order_by(AssessmentAttempt.created_at.desc()).all()
    
    # NO NEED to calculate anything here - it's done in the model properties
    # Remove ALL the code that was trying to set: 
    # attempt.time_taken_minutes, attempt.time_taken_seconds, attempt.parsed_answers
    
    return render_template("admin/dashboard.html", attempts=attempts)

@admin.route("/view/<int:attempt_id>")
def view_attempt(attempt_id):
    """View detailed attempt results"""
    attempt = AssessmentAttempt.query.get(attempt_id)
    if not attempt:
        return "Attempt not found", 404
    
    # Load questions for this assessment
    questions = load_questions(attempt.assessment_type)
    
    # Parse user answers using the model's parsed_answers property
    user_answers = attempt.parsed_answers  # This uses the @property from models.py
    
    # Prepare detailed score information
    score_details = []
    for q_num_str, user_answer in user_answers.items():
        q_num = int(q_num_str) - 1
        
        if q_num < len(questions):
            question = questions[q_num]
            
            # Determine if correct
            is_correct = False
            if question["question_type"] == "radio":
                correct_answer = question["correct_answers"][0] if question["correct_answers"] else ""
                is_correct = str(user_answer).strip() == str(correct_answer).strip()
            elif question["question_type"] == "checkbox":
                if isinstance(user_answer, list):
                    user_sorted = sorted([str(a).strip() for a in user_answer])
                    correct_sorted = sorted([str(a).strip() for a in question["correct_answers"]])
                    is_correct = (user_sorted == correct_sorted)
            
            score_details.append({
                "question": int(q_num_str),
                "question_text": question["question"],
                "question_type": question["question_type"],
                "options": question.get("options", []),
                "user_answer": user_answer,
                "correct_answer": question.get("correct_answers", []),
                "is_correct": is_correct,
                "points": question.get("points", 5)
            })
    
    # Sort by question number
    score_details.sort(key=lambda x: x["question"])
    
    return render_template("admin/view_attempt.html",
                         attempt=attempt,
                         score_details=score_details)

@admin.route("/export/csv")
def export_csv():
    """Export all attempts as CSV"""
    attempts = AssessmentAttempt.query.all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Email', 'Score', 'Total Questions', 
        'Percentage', 'Date', 'Answers'
    ])
    
    # Write data rows
    for attempt in attempts:
        writer.writerow([
            attempt.id,
            attempt.user_email,
            attempt.score,
            attempt.total_questions,
            attempt.percentage,
            attempt.created_at.strftime('%Y-%m-%d %H:%M'),
            attempt.answers  # JSON string
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=ifix_assessments.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

# Add delete route
@admin.route("/delete/<int:attempt_id>", methods=["POST"])
def delete_attempt(attempt_id):
    """Delete an assessment attempt"""
    attempt = AssessmentAttempt.query.get(attempt_id)
    if attempt:
        db.session.delete(attempt)
        db.session.commit()
        return jsonify({"success": True, "message": f"Attempt #{attempt_id} deleted"})
    return jsonify({"success": False, "message": "Attempt not found"}), 404

# Add report route
@admin.route("/report/<int:attempt_id>")
def generate_report(attempt_id):
    """Generate proctor report for an attempt"""
    attempt = AssessmentAttempt.query.get(attempt_id)
    if not attempt:
        return "Attempt not found", 404
    
    # You can create a detailed report here
    return f"Proctor report for attempt #{attempt_id} - {attempt.user_name}"