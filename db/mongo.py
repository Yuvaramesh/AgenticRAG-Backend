from http import client
from pymongo import MongoClient
from config import MONGO_CONNECTION_STRING, CA_FILE

# Initialize MongoClient with TLS CA file for secure connections
mongo_client = MongoClient(MONGO_CONNECTION_STRING, tlsCAFile=CA_FILE)
mongo_db = mongo_client["AgenticRag"] # Your database name

# Define collections
users_collection = mongo_db["users"]
sections_collection = mongo_db["sections"]
quizzes_collection = mongo_db["quizzes"]
chat_collection = mongo_db["ChatHistory"] # Example collection for chat history
documents_collection = mongo_db["documents"] # For Qdrant integration
mongo = client 