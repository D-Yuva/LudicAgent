import os
import traceback
import requests
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from ag2 import ConversableAgent, LLMConfig

# --- App & Agent Setup ---
app = FastAPI()

# Initialize your Gemini-powered AutoGen agent
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
MCP_SERVER = os.environ["MCP_SERVER"]  # e.g., https://a2-a-mcp.vercel.app

llm_config = LLMConfig(
    api_type="google",
    api_key=GEMINI_API_KEY,
    model="models/gemini-1.5-pro-latest"
)
agent = ConversableAgent(name="ludicagent", llm_config=llm_config)

# --- Models ---
class RelayMessage(BaseModel):
    session_id: str
    message: str

# --- Routes ---
@app.get("/favicon.png", include_in_schema=False)
async def favicon():
    return PlainTextResponse(status_code=204)

@app.post("/receive")
def receive_from_mcp(body: RelayMessage):
    try:
        print("📥 Received:", body)
        # Generate response via Gemini
        reply = agent.generate_reply([{"role": "user", "content": body.message}])
        print("🤖 Reply:", reply)

        # Flip session_id to reply back to courseagent
        flipped = ":".join(reversed(body.session_id.split(":", 1)))
        resp = requests.post(f"{MCP_SERVER}/relay", json={
            "session_id": flipped,
            "message": reply
        })
        print("📤 Replied via MCP:", resp.status_code, resp.text)

        return {"status": "replied", "to": flipped}
    except Exception as e:
        print("‼️ Receive Error:", e)
        traceback.print_exc()
        raise

# Optional: root health check
@app.get("/")
def health():
    return {"status": "alive", "agent": "ludicagent"}
