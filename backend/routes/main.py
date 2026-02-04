import json
import os
from database import db
from models import AssessmentAttempt
from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/select-assessment")
def select_assessment():
    """Show assessment type selection"""
    return render_template("select_assessment.html")

@main.route("/start")
def start_assessment():
    """Start assessment - redirect to assessment selection"""
    return redirect("/select-assessment")

@main.route("/register")
def register():
    """Show registration form"""
    assessment_type = request.args.get("assessment_type", "Excel Assessment")
    return render_template("register.html", assessment_type=assessment_type)

@main.route("/start-assessment", methods=["POST"])
def process_registration():
    """Process registration and start assessment"""
    # Store user info in session
    session["user_info"] = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "business": request.form.get("business"),
        "phone": request.form.get("phone"),
        "assessment_type": request.form.get("assessment_type")
    }
    
    # Initialize answers session
    session["answers"] = {}
    
    # Store start time
    session["start_time"] = datetime.now().isoformat()
    
    # Redirect to first question
    return redirect("/question/1")

@main.route("/question/<int:question_number>", methods=["GET", "POST"])
def question(question_number):
    """Show a single question dynamically"""
    
    user_info = session.get("user_info", {})
    if not user_info:
        return redirect("/select-assessment")
    
    assessment_type = user_info.get("assessment_type")
    
    # Load questions for this assessment type
    questions = load_questions(assessment_type)
    
    if not questions:
        return render_template("error.html", 
                             message="No questions found for this assessment type. Please contact support.")
    
    total_questions = len(questions)
    
    # Check if question exists
    if question_number > total_questions or question_number < 1:
        return redirect("/finish")
    
    # Get the current question (adjust for zero-based index)
    current_question = questions[question_number - 1]
    
    # Handle answer submission
    if request.method == "POST":
        answers_dict = session.get("answers", {})
        
        if current_question.get("question_type") == "checkbox":
            # For checkbox questions (multiple answers)
            selected_indices = request.form.getlist("answer")
            
            # Convert indices to option texts
            selected_answers = []
            for idx in selected_indices:
                try:
                    idx_int = int(idx)
                    if 0 <= idx_int < len(current_question["options"]):
                        selected_answers.append(current_question["options"][idx_int])
                except ValueError:
                    # If it's already text, use it directly
                    selected_answers.append(idx)
            
            answers_dict[str(question_number)] = selected_answers
            
        elif current_question.get("question_type") == "text":
            # For text input questions
            answer = request.form.get("answer", "").strip()
            answers_dict[str(question_number)] = answer
            
        else:
            # For radio button questions (single answer)
            answer = request.form.get("answer", "")
            
            # Convert index to option text if needed
            if answer.isdigit():
                try:
                    idx = int(answer)
                    if 0 <= idx < len(current_question["options"]):
                        answer = current_question["options"][idx]
                except ValueError:
                    pass  # Keep as is if conversion fails
            
            answers_dict[str(question_number)] = answer
        
        # Save answers to session
        session["answers"] = answers_dict
        
        # Debug output
        print(f"📝 Question {question_number} answer stored:")
        print(f"   Answer: {answers_dict[str(question_number)]}")
        print(f"   Type: {current_question.get('question_type')}")
        print(f"   Points: {current_question.get('points', 5)}")
        
        # Go to next question or finish
        if question_number < total_questions:
            return redirect(f"/question/{question_number + 1}")
        else:
            return redirect("/finish")
    
    return render_template("question.html",
                         question_number=question_number,
                         total_questions=total_questions,
                         question=current_question,
                         assessment_type=assessment_type)

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

def calculate_score(user_answers, questions):
    """Calculate score based on user answers"""
    correct_count = 0
    score_details = []
    
    for q_num_str, user_answer in user_answers.items():
        try:
            q_num = int(q_num_str) - 1
            
            if q_num >= len(questions):
                continue
                
            question = questions[q_num]
            
            # Skip questions with 0 points (don't count towards score)
            if question.get("points", 5) == 0:
                score_details.append({
                    "question": q_num + 1,
                    "user_answer": user_answer,
                    "correct_answer": question.get("correct_answers", []),
                    "points": 0,
                    "is_correct": None,  # Not applicable
                    "skipped": True
                })
                continue
            
            is_correct = False
            
            if question["question_type"] == "radio":
                # Single answer question
                correct_answer = question["correct_answers"][0] if question["correct_answers"] else ""
                
                # Normalize for comparison
                user_answer_normalized = str(user_answer).strip()
                correct_answer_normalized = str(correct_answer).strip()
                
                is_correct = (user_answer_normalized == correct_answer_normalized)
                
            elif question["question_type"] == "checkbox":
                # Multiple answer question
                if isinstance(user_answer, list):
                    # Sort and normalize both lists
                    user_answers_sorted = sorted([str(a).strip() for a in user_answer])
                    correct_answers_sorted = sorted([str(a).strip() for a in question["correct_answers"]])
                    is_correct = (user_answers_sorted == correct_answers_sorted)
                else:
                    # If not a list, check if it matches any single correct answer
                    is_correct = str(user_answer).strip() in [str(a).strip() for a in question["correct_answers"]]
            
            elif question["question_type"] == "text":
                # Text answers - usually not scored
                is_correct = False  # Text answers typically don't have correct/incorrect
            
            if is_correct:
                correct_count += 1
            
            score_details.append({
                "question": q_num + 1,
                "user_answer": user_answer,
                "correct_answer": question.get("correct_answers", []),
                "points": question.get("points", 5),
                "is_correct": is_correct,
                "skipped": False
            })
            
        except Exception as e:
            print(f"❌ Error scoring question {q_num_str}: {e}")
            continue
    
    return correct_count, score_details

# DELETE THE FIRST finish() FUNCTION AND KEEP THIS ONE
@main.route("/finish", methods=["GET", "POST"])
def finish():
    """Show results after assessment completion"""
    
    # Get user info from session
    user_info = session.get("user_info", {})
    user_answers = session.get("answers", {})
    
    if not user_info:
        return redirect("/select-assessment")
    
    assessment_type = user_info.get("assessment_type")
    
    # Load questions for this assessment type
    questions = load_questions(assessment_type)
    
    # Debug: Show all questions and answers
    print(f"🔍 DEBUG: Assessment Type: {assessment_type}")
    print(f"🔍 DEBUG: Total Questions in JSON: {len(questions)}")
    print(f"🔍 DEBUG: User Answers: {json.dumps(user_answers, indent=2)}")
    
    # Calculate score
    correct_count, score_details = calculate_score(user_answers, questions)
    
    # Count only questions that have points > 0
    scored_questions = [q for q in questions if q.get("points", 5) > 0]
    total_scored_questions = len(scored_questions)
    
    # Calculate percentage based on scored questions only
    if total_scored_questions > 0:
        percentage = int((correct_count / total_scored_questions) * 100)
    else:
        percentage = 0
    
    # Debug output
    print(f"📊 SCORING RESULTS:")
    print(f"   Total questions: {len(questions)}")
    print(f"   Scored questions: {total_scored_questions}")
    print(f"   Correct answers: {correct_count}")
    print(f"   Percentage: {percentage}%")
    print(f"   Passed: {percentage >= 70}")
    
    # Show detailed scoring for debugging
    for detail in score_details:
        if not detail.get("skipped", False):
            print(f"   Q{detail['question']}: User='{detail['user_answer']}' | Correct='{detail['correct_answer']}' | Correct={detail['is_correct']}")
    
    # Save to database WITH USER INFO
    attempt = AssessmentAttempt(
        user_name=user_info.get("name"),
        user_email=user_info.get("email"),
        user_business=user_info.get("business"),
        user_phone=user_info.get("phone"),
        assessment_type=assessment_type,
        score=correct_count,
        total_questions=total_scored_questions,  # Use scored questions count
        percentage=percentage,
        answers=json.dumps(user_answers),
        started_at=datetime.fromisoformat(session.get("start_time", datetime.now().isoformat())),
        completed_at=datetime.now(),
        created_at=datetime.now()
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    # Send email to user
    try:
        from services.email_service import send_assessment_results
        send_assessment_results(attempt, user_info.get("email"))
        email_sent = True
    except Exception as e:
        print(f"Email error: {e}")
        email_sent = False
    
    # Store attempt ID for PDF download
    session["last_attempt_id"] = attempt.id
    session["attempt_passed"] = percentage >= 70
    
    # Clear answers but keep user info for potential retry
    session.pop("answers", None)
    session.pop("start_time", None)
    
    # Calculate time taken for display
    time_taken = attempt.completed_at - attempt.started_at
    
    return render_template("assessment_complete.html", 
                         attempt=attempt,
                         email_sent=email_sent,
                         passed=percentage >= 70,
                         time_taken=time_taken)  # Pass time_taken to template

@main.route("/download-certificate", methods=["POST"])
def download_certificate():
    """Generate and download PDF certificate"""
    attempt_id = request.form.get("attempt_id")
    
    if not attempt_id:
        return "No attempt ID provided", 400
    
    # Get attempt from database
    attempt = AssessmentAttempt.query.get(attempt_id)
    if not attempt:
        return "Attempt not found", 404
    
    # Check if passed
    if attempt.percentage < 70:
        return "Certificate only available for passing attempts (70%+)", 403
    
    # Generate PDF
    try:
        from services.pdf_service import generate_certificate
        pdf_buffer = generate_certificate(attempt)
        
        # Create response
        from flask import send_file
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"IFIX_Certificate_{attempt.user_name}_{attempt.id}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Certificate generation error: {e}")
        return f"Error generating certificate: {e}", 500

@main.route("/results")
def results():
    """Redirect to finish page"""
    return redirect("/finish")

@main.route("/health")
def health():
    return "System is running ✅"