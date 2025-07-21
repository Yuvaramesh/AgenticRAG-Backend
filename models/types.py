from typing import TypedDict, List, Optional
import enum
import json
from bson.objectid import ObjectId 
from datetime import datetime
from pydantic import BaseModel, Field

class UserRole(enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: str
    password: Optional[str] = None
    name: Optional[str] = None
    role: str = "student" 
    preferred_languages: List[str] = ["en"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    image: Optional[str] = None

    class Config:
        populate_by_name = True 
        arbitrary_types_allowed = True 
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z", 
            ObjectId: lambda oid: str(oid)
        }

class Section(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    description: Optional[str] = None
    teacher_id: str 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z",
            ObjectId: lambda oid: str(oid)
        }

class Question(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: str 

class Quiz(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    description: Optional[str] = None
    section_id: Optional[str] = None 
    created_by: str 
    questions: List[Question] 
    is_enabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z",
            ObjectId: lambda oid: str(oid)
        }

class Document(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    filename: str
    file_path: str
    qdrant_id: Optional[str] = None 
    uploaded_by: str 
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {} 

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z",
            ObjectId: lambda oid: str(oid)
        }

class ChatMessage(BaseModel):
    role: str 
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatState(TypedDict):
    query: str
    selected_file: Optional[str]
    context_chunks: List[str]
    agent_type: Optional[str]
    answer: Optional[str]
    user_email: str
    chat_history: List[ChatMessage] 
    image_path: Optional[str]

class ChatSession(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z",
            ObjectId: lambda oid: str(oid)
        }

class QuizAttempt(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    student_id: str
    quiz_id: str
    score: int
    total_questions: int
    attempt_date: datetime = Field(default_factory=datetime.utcnow)
    answers: dict 
    time_taken: Optional[int] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z",
            ObjectId: lambda oid: str(oid)
        }

class ActivitySubmission(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    student_id: str
    activity_id: str
    submission_date: datetime = Field(default_factory=datetime.utcnow)
    grade: Optional[int] = None
    feedback: Optional[str] = None
    status: str 

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z",
            ObjectId: lambda oid: str(oid)
        }

class PublishSchedule(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    quiz_id: Optional[str] = None
    activity_id: Optional[str] = None
    publish_date: datetime
    unpublish_date: Optional[datetime] = None
    target_sections: List[str] 
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str 

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z",
            ObjectId: lambda oid: str(oid)
        }


def doc_to_dict(doc):
    if not doc:
        return None
    
    doc_copy = dict(doc)

    if '_id' in doc_copy:
        doc_copy['id'] = str(doc_copy['_id'])
        del doc_copy['_id']

    for key, value in doc_copy.items():
        if isinstance(value, ObjectId):
            doc_copy[key] = str(value)
        elif isinstance(value, list):
            doc_copy[key] = [str(item) if isinstance(item, ObjectId) else item for item in value]
        elif isinstance(value, datetime):
            doc_copy[key] = value.isoformat() + "Z" 
    if 'questions' in doc_copy and isinstance(doc_copy['questions'], list):
        for q in doc_copy['questions']:
            if 'options' in q and isinstance(q['options'], str):
                try:
                    q['options'] = json.loads(q['options'])
                except json.JSONDecodeError:
                    pass
    
    if 'answers' in doc_copy and isinstance(doc_copy['answers'], str):
        try:
            doc_copy['answers'] = json.loads(doc_copy['answers'])
        except json.JSONDecodeError:
            pass

    if 'role' in doc_copy and isinstance(doc_copy['role'], UserRole):
        doc_copy['role'] = doc_copy['role'].value
    
    if 'preferred_languages' in doc_copy and isinstance(doc_copy['preferred_languages'], str):
        try:
            doc_copy['preferred_languages'] = json.loads(doc_copy['preferred_languages'])
        except json.JSONDecodeError:
            pass

    return doc_copy

def prepare_data_for_mongo(data):
    if 'id' in data and data['id']:
        try:
            data['_id'] = ObjectId(data['id'])
            del data['id']
        except Exception:
            pass 

    for key in ['teacher_id', 'created_by', 'section_id', 'uploaded_by', 'user_id', 'student_id', 'activity_id', 'quiz_id']:
        if key in data and data[key] is not None and isinstance(data[key], str):
            try:
                data[key] = ObjectId(data[key])
            except Exception:
                pass 

    if 'target_sections' in data and isinstance(data['target_sections'], list):
        data['target_sections'] = [ObjectId(s_id) if isinstance(s_id, str) else s_id for s_id in data['target_sections']]

    if 'questions' in data and isinstance(data['questions'], list):
        data['questions'] = [q.dict() if isinstance(q, BaseModel) else q for q in data['questions']]
        for q in data['questions']:
            if 'options' in q and isinstance(q['options'], list):
                q['options'] = json.dumps(q['options']) 
    
    if 'answers' in data and isinstance(data['answers'], dict):
        data['answers'] = json.dumps(data['answers']) 
    if 'messages' in data and isinstance(data['messages'], list):
        data['messages'] = [m.dict() if isinstance(m, BaseModel) else m for m in data['messages']]

    return data
