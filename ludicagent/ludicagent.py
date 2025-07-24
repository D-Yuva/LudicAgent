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
    input_msg = body.message
    session_id = body.session_id
    response = agent.generate_reply([{"role": "user", "content": input_msg}])
    flipped = ":".join(reversed(session_id.split(":")))
    requests.post(f"{MCP_SERVER}/relay", json={
        "session_id": flipped,
        "message": response
    })
    return {"status": "replied", "to": flipped}
