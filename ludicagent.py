import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from autogen import ConversableAgent, LLMConfig

# Agent Setup
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
MCP_SERVER = os.environ["MCP_SERVER"]
AGENT_NAME = "ludicagent"

llm_config = LLMConfig(
    api_type="google",
    api_key=GEMINI_KEY,
    model="models/gemini-1.5-pro-latest"
)
agent = ConversableAgent(name=AGENT_NAME, llm_config=llm_config)

app = FastAPI()

class RelayMessage(BaseModel):
    session_id: str
    message: str

@app.post("/receive")
def receive_from_mcp(body: RelayMessage):
    try:
        print("📥 Received:", body)
        response = agent.generate_reply([{"role":"user","content":body.message}])
        flipped = ":".join(reversed(body.session_id.split(":")))
        resp = requests.post(f"{MCP_SERVER}/relay", json={
            "session_id": flipped,
            "message": response
        })
        print("📤 Replied via MCP:", resp.status_code, resp.text)
        return {"status":"replied", "to": flipped}
    except Exception as e:
        print("‼️ /receive error:", repr(e))
        raise

