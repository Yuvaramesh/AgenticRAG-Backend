from werkzeug.security import generate_password_hash
from db.mongo import mongo_db
from datetime import datetime

def create_test_users():
    # Create admin user
    admin_user = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": generate_password_hash("admin123"),
        "role": "admin",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Create teacher user
    teacher_user = {
        "name": "Teacher User",
        "email": "teacher@example.com", 
        "password": generate_password_hash("teacher123"),
        "role": "teacher",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Create student user
    student_user = {
        "name": "Student User",
        "email": "student@example.com",
        "password": generate_password_hash("student123"),
        "role": "student", 
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Check if users already exist
    if not mongo_db.users.find_one({"email": "admin@example.com"}):
        mongo_db.users.insert_one(admin_user)
        print("Admin user created: admin@example.com / admin123")
    
    if not mongo_db.users.find_one({"email": "teacher@example.com"}):
        mongo_db.users.insert_one(teacher_user)
        print("Teacher user created: teacher@example.com / teacher123")
        
    if not mongo_db.users.find_one({"email": "student@example.com"}):
        mongo_db.users.insert_one(student_user)
        print("Student user created: student@example.com / student123")

if __name__ == "__main__":
    create_test_users()
