from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from database.database import engine, Base
from database.models import User, Student # Imported for Alembic metadata
from auth.router import router as auth_router
from api.profile import router as profile_router
from api.courses.router import router as courses_router
from api.activities.router import router as activities_router
from api.plan.router import router as plan_router
from api.chat.router import router as chat_router, router_ws as chat_ws_router
from api.documents.router import router as documents_router
from utils.limiter import limiter

app = FastAPI(
    title="Multi-Agent Strategic Planning Platform",
    description="API for college applicants multi-tenant platform with AI agents.",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(courses_router, prefix="/api")
app.include_router(activities_router, prefix="/api")
app.include_router(plan_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(chat_ws_router)   # WebSocket: /ws/chat (no /api prefix)
app.include_router(documents_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi-Agent Strategic Planning API. Please visit /docs for API documentation."}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
