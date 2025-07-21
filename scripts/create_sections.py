from db.mongo import mongo_db
from bson.objectid import ObjectId
from datetime import datetime

def create_default_sections():
    # First, get teacher users
    teachers = list(mongo_db.users.find({"role": "teacher"}))
    
    if not teachers:
        print("No teachers found. Please create teacher users first.")
        return
    
    # Create default sections
    default_sections = [
        {"name": "Mathematics", "teacher_id": teachers[0]["_id"]},
        {"name": "Science", "teacher_id": teachers[0]["_id"]},
        {"name": "English", "teacher_id": teachers[0]["_id"]},
    ]
    
    for section_data in default_sections:
        # Check if section already exists
        existing_section = mongo_db.sections.find_one({"name": section_data["name"]})
        if not existing_section:
            section_data.update({
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            result = mongo_db.sections.insert_one(section_data)
            print(f"Created section: {section_data['name']} with ID: {result.inserted_id}")
        else:
            print(f"Section {section_data['name']} already exists")

if __name__ == "__main__":
    create_default_sections()
