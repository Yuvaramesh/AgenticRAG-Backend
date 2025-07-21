from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from auth_decorators import role_required
from db.mongo import mongo_db
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import statistics
from bson.json_util import dumps
student_stats_bp = Blueprint("student_stats", __name__)

@student_stats_bp.route("/quiz-results", methods=["POST"])
@cross_origin(origins=["http://localhost:3000"])
# @role_required(["student"])
def submit_quiz_results():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'topic_id', 'correct_answer', 'wrong_answer']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'success': False
                }), 400
        
        # Validate data types
        try:
            student_id = ObjectId(str(data['student_id']))
            topic_id = ObjectId(str(data['topic_id']))
            correct_answer = int(data['correct_answer'])
            wrong_answer = int(data['wrong_answer'])
        except (ValueError, TypeError) as e:
            return jsonify({
                'error': 'Invalid data types provided',
                'success': False
            }), 400
        
        # Validate non-negative values
        if correct_answer < 0 or wrong_answer < 0:
            return jsonify({
                'error': 'Correct and wrong answers must be non-negative',
                'success': False
            }), 400
        
        # Calculate total questions and score
        total_questions = correct_answer + wrong_answer
        score_percentage = (correct_answer / total_questions * 100) if total_questions > 0 else 0
        
        # Create quiz result document
        quiz_result = {
            'student_id': student_id,
            'topic_id': topic_id,
            'correct_answer': correct_answer,
            'wrong_answer': wrong_answer,
            'total_questions': total_questions,
            'score_percentage': round(score_percentage, 2),
            'submitted_at': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert into MongoDB
        result = mongo_db.quizz_result.insert_one(quiz_result)
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Quiz results submitted successfully',
            'result_id': str(result.inserted_id),
            'data': {
                'correct_answer': correct_answer,
                'wrong_answer': wrong_answer,
                'total_questions': total_questions,
                'score_percentage': score_percentage,
                'submitted_at': quiz_result['submitted_at'].isoformat()
            }
        }), 201
        
    except Exception as e:
        print(f"Error submitting quiz results: {e}")
        return jsonify({
            'error': 'Internal server error',
            'success': False
        }), 500

@student_stats_bp.route("/student_performance", methods=["GET"])
@cross_origin(origins=["http://localhost:3000"])
@role_required(["student"])
def get_student_performance(current_user):
    student_id = ObjectId(current_user['id'])
    
    # Get quiz attempts for the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    quiz_attempts = list(mongo_db.quiz_attempts.find({
        "student_id": student_id,
        "attempt_date": {"$gte": thirty_days_ago}
    }).sort("attempt_date", 1))
    
    # Get activity submissions for the last 30 days
    activity_submissions = list(mongo_db.activity_submissions.find({
        "student_id": student_id,
        "submission_date": {"$gte": thirty_days_ago},
        "grade": {"$exists": True}
    }).sort("submission_date", 1))
    
    # Create performance data points
    performance_data = []
    
    # Group by date and calculate averages
    date_quiz_scores = {}
    date_activity_grades = {}
    
    for attempt in quiz_attempts:
        date_str = attempt['attempt_date'].strftime('%Y-%m-%d') if isinstance(attempt['attempt_date'], datetime) else attempt['attempt_date'][:10]
        score_percentage = (attempt['score'] / attempt['total_questions']) * 100
        
        if date_str not in date_quiz_scores:
            date_quiz_scores[date_str] = []
        date_quiz_scores[date_str].append(score_percentage)
    
    for submission in activity_submissions:
        date_str = submission['submission_date'].strftime('%Y-%m-%d') if isinstance(submission['submission_date'], datetime) else submission['submission_date'][:10]
        
        if date_str not in date_activity_grades:
            date_activity_grades[date_str] = []
        date_activity_grades[date_str].append(submission['grade'])
    
    # Combine dates and create data points
    all_dates = set(list(date_quiz_scores.keys()) + list(date_activity_grades.keys()))
    
    for date_str in sorted(all_dates):
        quiz_avg = statistics.mean(date_quiz_scores[date_str]) if date_str in date_quiz_scores else 0
        activity_avg = statistics.mean(date_activity_grades[date_str]) if date_str in date_activity_grades else 0
        
        performance_data.append({
            "date": date_str,
            "quiz_score": round(quiz_avg, 1),
            "activity_grade": round(activity_avg, 1)
        })
    
    return jsonify(performance_data)

@student_stats_bp.route("/quiz-results", methods=["GET"])
@cross_origin(origins=["http://localhost:3000"])
def get_all_quiz_results():
    pipeline = [
    {
        "$lookup": {
            "from": "users",
            "localField": "student_id",
            "foreignField": "_id",
            "as": "student"
        }
    },
    {
        "$unwind": "$student"
    },
    {
        "$lookup": {
            "from": "quizzes",
            "localField": "topic_id",
            "foreignField": "_id",
            "as": "quiz"
        }
    },
    {
        "$unwind": "$quiz"
    },
    {
        "$project": {
            "student_name": "$student.name",
            "quiz_title": "$quiz.title",
            "correct_answer":1,
            "wrong_answer":1,
            "total_questions":1,
            "score_percentage":1,
            "submitted_at":1,
            "created_at":1,
            "updated_at":1
            }
    }
    ]

    results = list(mongo_db.quizz_result.aggregate(pipeline))
    return dumps(results)  # returns a JSON string