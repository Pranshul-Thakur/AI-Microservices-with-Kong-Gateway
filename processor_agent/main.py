from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

class Document(BaseModel):
    id: str
    content: str

class ProcessRequest(BaseModel):
    documents: List[Document]

@app.post("/process")
async def process_documents(request: ProcessRequest):
    if not request.documents:
        raise HTTPException(status_code=400, detail="No documents provided for processing.")

    summary = " ".join([doc.content[:30] + "..." for doc in request.documents])
    return {
        "summary": summary.strip(),
        "label": "AI_PROCESSED"
    }