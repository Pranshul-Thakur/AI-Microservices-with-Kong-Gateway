import uuid
import httpx
import json
import logging
import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.FileHandler(os.path.join(LOG_DIR, "audit.jsonl"))]
)

app = FastAPI()

IDEMPOTENCY_CACHE = {}

class ProcessRequest(BaseModel):
    request_id: str
    query: str

@app.post("/process-request")
async def process_request(request: ProcessRequest, http_request: Request):
    trace_id = str(uuid.uuid4())
    log_data = {
        "trace_id": trace_id,
        "request_id": request.request_id,
        "api_key_consumer": http_request.headers.get("X-Consumer-Username", "unknown"),
    }

    if request.request_id in IDEMPOTENCY_CACHE:
        log_data["status"] = "cache_hit"
        logging.info(json.dumps(log_data))
        return IDEMPOTENCY_CACHE[request.request_id]

    async with httpx.AsyncClient() as client:
        try:
            retriever_response = await client.post(
                "http://retriever_agent:8000/retrieve", 
                json={"query": request.query}
            )
            retriever_response.raise_for_status()
            documents = retriever_response.json().get("documents", [])
        except httpx.RequestError as e:
            log_data["status"] = "retriever_failed"
            logging.info(json.dumps(log_data))
            raise HTTPException(status_code=503, detail=f"Retriever service unavailable: {e}")

    async with httpx.AsyncClient() as client:
        try:
            processor_response = await client.post(
                "http://processor_agent:8000/process", 
                json={"documents": documents}
            )
            processor_response.raise_for_status()
            processed_data = processor_response.json()
        except httpx.RequestError as e:
            log_data["status"] = "processor_failed"
            logging.info(json.dumps(log_data))
            raise HTTPException(status_code=503, detail=f"Processor service unavailable: {e}")

    final_response = {
        "request_id": request.request_id,
        "summary": processed_data.get("summary"),
        "label": processed_data.get("label"),
        "trace_id": trace_id
    }
    
    IDEMPOTENCY_CACHE[request.request_id] = final_response
    log_data["status"] = "success"
    logging.info(json.dumps(log_data))

    return final_response