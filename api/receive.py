import os
import traceback
import requests
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from google import genai  # GemMI API client

app = FastAPI()

# Initialize Gemini GenAI client
genai_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Environment
MCP_SERVER = os.environ["MCP_SERVER"]

class RelayMessage(BaseModel):
    session_id: str
    message: str

@app.get("/favicon.png", include_in_schema=False)
async def favicon():
    return PlainTextResponse(status_code=204)

@app.get("/")
def health():
    return {"status": "alive", "agent": "ludicagent"}

@app.post("/receive")
def receive_from_mcp(body: RelayMessage):
    try:
        print("📥 Received:", body)
        
        # Generate text using Gemini
        resp = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=body.message
        )
        reply = resp.text
        print("🤖 Reply:", reply)

        # Flip session_id to route back
        session, _ = body.session_id.split(":", 1)
        flipped = f"{session}:courseagent"

        # Relay via MCP
        r = requests.post(f"{MCP_SERVER}/relay", json={
            "session_id": flipped,
            "message": reply
        })
        print("📤 Relayed:", r.status_code, r.text)
        return {"status": "replied", "to": flipped}

    except Exception as e:
        print("‼️ Error in /receive:", e)
        traceback.print_exc()
        raise
