from fastapi import FastAPI, Response, status
from pydantic import BaseModel

app = FastAPI()

class PolicyRequest(BaseModel):
    query: str

@app.post("/policy")
async def check_policy(request: PolicyRequest, response: Response):
    if "forbidden" in request.query.lower():
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"allow": False, "reason": "Query contains a forbidden word."}
    return {"allow": True}