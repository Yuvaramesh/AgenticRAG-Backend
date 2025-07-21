from config import MONGO_CONNECTION_STRING, CA_FILE
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash

# Connect to MongoDB
try:
    client = MongoClient(MONGO_CONNECTION_STRING, tlsCAFile=CA_FILE)
    db = client["AgenticRag"]  # Your database name
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

# Define collections
users_collection = db["users"]
sections_collection = db["sections"]
quizzes_collection = db["quizzes"]
chat_collection = db["chat_history"]
documents_collection = db["documents"]
activity_submissions_collection = db["activity_submissions"] # Added for completeness
quiz_attempts_collection = db["quiz_attempts"] # Added for completeness
publish_schedules_collection = db["publish_schedules"] # Added for completeness


def seed_data():
    print("Seeding initial data...")
    # Clear existing data
    users_collection.drop()
    sections_collection.drop()
    quizzes_collection.drop()
    chat_collection.drop()
    documents_collection.drop()
    activity_submissions_collection.drop() # Drop new collections too
    quiz_attempts_collection.drop()
    publish_schedules_collection.drop()
    print("Dropped existing collections.")

    # Seed Users
    admin_obj_id = ObjectId()
    teacher_obj_id = ObjectId()
    student_obj_id = ObjectId()

    users_data = [
        {"_id": admin_obj_id, "email": "admin@example.com", "name": "Admin User", "role": "admin", "password": generate_password_hash("admin123")},
        {"_id": teacher_obj_id, "email": "teacher@example.com", "name": "Teacher Jane", "role": "teacher", "password": generate_password_hash("teacher123")},
        {"_id": student_obj_id, "email": "student@example.com", "name": "Student John", "role": "student", "password": generate_password_hash("student123")},
    ]
    users_collection.insert_many(users_data)
    print(f"Seeded {len(users_data)} users.")

    # Seed Sections
    section1_obj_id = ObjectId()
    section2_obj_id = ObjectId()
    sections_data = [
        {"_id": section1_obj_id, "name": "Introduction to AI", "description": "Basics of Artificial Intelligence.", "teacher_id": teacher_obj_id, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
        {"_id": section2_obj_id, "name": "Advanced Machine Learning", "description": "Deep dive into ML algorithms.", "teacher_id": teacher_obj_id, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
    ]
    sections_collection.insert_many(sections_data)
    print(f"Seeded {len(sections_data)} sections.")

    # Seed Quizzes
    quiz1_obj_id = ObjectId()
    quiz2_obj_id = ObjectId()
    quizzes_data = [
        {
            "_id": quiz1_obj_id,
            "title": "AI Fundamentals Quiz",
            "description": "Quiz on basic AI concepts.",
            "section_id": section1_obj_id, # Use ObjectId
            "created_by": teacher_obj_id, # Use ObjectId
            "is_enabled": True, # Set to True for students to see it
            "questions": [
                {"question_text": "What does AI stand for?", "options": ["Artificial Intelligence", "Automated Information", "Advanced Integration", "Algorithmic Innovation"], "correct_answer": "Artificial Intelligence"},
                {"question_text": "Which of these is a type of AI?", "options": ["Machine Learning", "Data Storage", "Cloud Computing", "Network Security"], "correct_answer": "Machine Learning"},
                {"question_text": "What is the goal of Artificial General Intelligence (AGI)?", "options": ["To perform specific tasks efficiently", "To mimic human-like intelligence across various tasks", "To process large datasets", "To automate repetitive jobs"], "correct_answer": "To mimic human-like intelligence across various tasks"},
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": quiz2_obj_id,
            "title": "ML Algorithms Quiz",
            "description": "Quiz on common machine learning algorithms.",
            "section_id": section2_obj_id, # Use ObjectId
            "created_by": teacher_obj_id, # Use ObjectId
            "is_enabled": False, # Keep as False for testing publishing
            "questions": [
                {"question_text": "What is a common supervised learning algorithm?", "options": ["K-Means", "Linear Regression", "PCA", "Apriori"], "correct_answer": "Linear Regression"},
                {"question_text": "Which algorithm is used for clustering?", "options": ["Decision Tree", "K-Means", "Support Vector Machine", "Naive Bayes"], "correct_answer": "K-Means"},
                {"question_text": "What does ' overfitting' mean in machine learning?", "options": ["Model performs well on training data but poorly on new data", "Model performs poorly on training data", "Model is too simple", "Model is too fast"], "correct_answer": "Model performs well on training data but poorly on new data"},
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(), # New quiz without section_id
            "title": "General Knowledge Quiz",
            "description": "A quiz on various general topics.",
            "section_id": None, # Explicitly set to None
            "created_by": teacher_obj_id,
            "is_enabled": True,
            "questions": [
                {"question_text": "What is the capital of France?", "options": ["Berlin", "Madrid", "Paris", "Rome"], "correct_answer": "Paris"},
                {"question_text": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "correct_answer": "Mars"},
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    quizzes_collection.insert_many(quizzes_data)
    print(f"Seeded {len(quizzes_data)} quizzes.")
    print("Data seeding complete!")

if __name__ == "__main__":
    seed_data()
    client.close()
    print("MongoDB connection closed.")
