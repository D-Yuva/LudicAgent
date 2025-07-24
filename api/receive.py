from fastapi import FastAPI
import traceback
from pydantic import BaseModel
import requests
from ag2 import ConversableAgent, LLMConfig

app = FastAPI()

# Initialize your Gemini agent
agent = ConversableAgent(...)

class RelayMessage(BaseModel):
    session_id: str
    message: str

@app.post("/receive")
def receive(body: RelayMessage):
    try:
        print("📥 Received:", body)
        reply = agent.generate_reply([{"role":"user","content":body.message}])
        print("🤖 Reply:", reply)
        ...
        return {"status": "replied"}
    except Exception as e:
        print("‼️ Receive Error:", e)
        traceback.print_exc()
        raise
