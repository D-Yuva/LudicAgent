import os
import traceback
import requests
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from groq import Groq

app = FastAPI()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MCP_SERVER = os.environ["MCP_SERVER"]  # e.g., https://a2-a-mcp.vercel.app

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

        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an informed instructor."},
                {"role": "user", "content": body.message}
            ],
            model="llama3-8b-8192"  # or choose "llama3-70b-8192" per your quota :contentReference[oaicite:1]{index=1}
        )
        reply = resp.choices[0].message.content
        print("🤖 Reply:", reply)

        session, _ = body.session_id.split(":", 1)
        flipped = f"{session}:courseagent"
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
