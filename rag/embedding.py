from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client.models import PointStruct
from qdrant_client import QdrantClient
import uuid
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
from sentence_transformers import SentenceTransformer

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

def embed_and_store(filename, content):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(content)
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=EMBED_MODEL.encode(chunk).tolist(),
            payload={"source": filename, "text": chunk}
        )
        for chunk in chunks
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(chunks)
