from pymongo import MongoClient
from config import MONGO_CONNECTION_STRING, CA_FILE

mongo_client = MongoClient(MONGO_CONNECTION_STRING, tlsCAFile=CA_FILE)
mongo_db = mongo_client["AgenticRag"]
chat_collection = mongo_db["ChatHistory"]
