from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DOCUMENTS = [
    {"id": "doc1", "content": "The first document is about artificial intelligence and machine learning."},
    {"id": "doc2", "content": "The second document discusses the future of space exploration and technology."},
    {"id": "doc3", "content": "This document covers advanced topics in deep learning and neural networks."},
    {"id": "doc4", "content": "A guide to building scalable microservices with Python and Docker."},
    {"id": "doc5", "content": "Exploring the ethics of artificial intelligence in modern society."}
]

class QueryRequest(BaseModel):
    query: str

@app.post("/retrieve")
async def retrieve_documents(request: QueryRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    query_words = set(request.query.lower().split())
    matching_docs = [
        doc for doc in DOCUMENTS if any(word in doc["content"].lower() for word in query_words)
    ]
    
    return {"documents": matching_docs[:3]}