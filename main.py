"""
Sephira Institute - Unified API
Serves both the Sephira Orion frontend and the external financial dashboard.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
import os

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create FastAPI app
app = FastAPI(
    title="Sephira Orion API",
    description="Unified API for Sephira Orion frontend and external dashboard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - allow all origins so both frontends can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Mount existing Sephira Orion backend routers (/api/chat, /api/predict, etc.)
# ---------------------------------------------------------------------------
try:
    from backend.api.routes import chat as sephira_chat, predictions, data
    app.include_router(sephira_chat.router)    # /api/chat
    app.include_router(predictions.router)      # /api/predict/*
    app.include_router(data.router)             # /api/data/*
    print("Sephira Orion backend routers mounted successfully.")
except Exception as e:
    print(f"Warning: Could not mount Sephira backend routers: {e}")
    print("The /api/* endpoints will not be available. Dashboard endpoints still work.")


# ---------------------------------------------------------------------------
# Health endpoint (used by the Sephira Orion frontend)
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "services": {"api": True},
    }


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Sephira Orion API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


# ===========================================================================
# External Dashboard Endpoints (new)
# ===========================================================================

DASHBOARD_SYSTEM_PROMPT = "You are a senior financial analyst at the Sephira Institute."


class CountryRequest(BaseModel):
    country: str


class DashboardChatRequest(BaseModel):
    country: str
    user_question: str


@app.post("/get_summary")
async def get_summary(request: CountryRequest):
    """Analyze current economic and geopolitical trends for a country."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": DASHBOARD_SYSTEM_PROMPT},
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
async def dashboard_chat(request: DashboardChatRequest):
    """Answer a financial question in the context of a country (dashboard)."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": DASHBOARD_SYSTEM_PROMPT},
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


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
