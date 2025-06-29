import os
from urllib.parse import quote_plus
import certifi

QDRANT_URL = "https://2ed85abb-e606-4167-8d2e-ce4185f33997.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.UYr-iYmbfZzhyr-lGQBlMlMuYQIAxriQhZd6af7vLq4"
COLLECTION_NAME = "agenticragbackend"
GEMINI_API_KEY = "AIzaSyC4cnVA6epWPvL39xUCDJxcHO67l4vbsOc"

mongo_username = "yuva"
mongo_raw_password = "yuva123"
mongo_password = quote_plus(mongo_raw_password)
MONGO_CONNECTION_STRING = (
    f"mongodb+srv://yuva2:{mongo_password}@cluster0.lujyqyz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

CA_FILE = certifi.where()
