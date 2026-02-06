"""
Sephira Institute - Financial Analysis Backend
Simplified REST API for the external dashboard.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create FastAPI app
app = FastAPI(
    title="Sephira Institute - Financial Analysis API",
    version="1.0.0",
)

# CORS - allow all origins so the frontend dashboard can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = "You are a senior financial analyst at the Sephira Institute."


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class CountryRequest(BaseModel):
    country: str


class ChatRequest(BaseModel):
    country: str
    user_question: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/get_summary")
async def get_summary(request: CountryRequest):
    """Analyze current economic and geopolitical trends for a country."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Analyze the current economic and geopolitical trends for {request.country}. "
                        "Return your analysis as a JSON object with exactly these keys: "
                        "\"long_term\" (analysis of the long-term trend), "
                        "\"short_term\" (analysis of the last year), "
                        "\"drivers\" (key economic drivers). "
                        "Return ONLY the JSON object, no markdown fences."
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000,
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)

        return {
            "long_term": parsed.get("long_term", "Analysis unavailable."),
            "short_term": parsed.get("short_term", "Analysis unavailable."),
            "drivers": parsed.get("drivers", "Analysis unavailable."),
        }

    except Exception as e:
        print(f"OpenAI error in /get_summary: {e}")
        return {
            "long_term": "Unable to generate long-term analysis at this time.",
            "short_term": "Unable to generate short-term analysis at this time.",
            "drivers": "Unable to determine key economic drivers at this time.",
        }


@app.post("/chat")
async def chat(request: ChatRequest):
    """Answer a financial question in the context of a country."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context: {request.country}. Question: {request.user_question}",
                },
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        answer = response.choices[0].message.content
        return {"answer": answer}

    except Exception as e:
        print(f"OpenAI error in /chat: {e}")
        return {"answer": "Unable to generate a response at this time. Please try again later."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
