# ---------------------------------------------------------
# 🌌 Lucid-Core Main Entry — FastAPI Application
# ---------------------------------------------------------
from fastapi import FastAPI
from Backend.app.routes import projects, plan, nodes, branches
from Backend.app.database import init_db
from Backend.app.config import settings

# ---------------------------------------------------------
# Initialize FastAPI App
# ---------------------------------------------------------
app = FastAPI(
    title="Lucid-Core",
    description="🧠 A Conversation Version Control System (CVCS) — like Git, but for AI reasoning and branching workflows.",
    version="1.0.0"
)

# ---------------------------------------------------------
# Environment Config Debugging
# ---------------------------------------------------------
print("\n🔧 Loaded Environment Configuration:")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"Redis URL: {settings.REDIS_URL}")
print(f"S3 Endpoint: {settings.S3_ENDPOINT}")
print(f"S3 Bucket: {settings.S3_BUCKET}")
print(f"OpenAI Key: {'✅ Present' if settings.OPENAI_API_KEY else '❌ Not Provided'}\n")

# ---------------------------------------------------------
# App Startup — Initialize DB
# ---------------------------------------------------------
@app.on_event("startup")
def on_startup():
    print("🚀 Initializing database...")
    init_db()
    print("✅ Database initialized successfully.\n")

# ---------------------------------------------------------
# Register Routers
# ---------------------------------------------------------
app.include_router(projects.router)
app.include_router(plan.router)
app.include_router(nodes.router)
app.include_router(branches.router)

# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "Lucid-Core"}

# ---------------------------------------------------------
# Root Route
# ---------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "🌌 Welcome to Lucid-Core — The AI Reasoning Version Control System.",
        "docs": "/docs",
        "health": "/health"
    }
