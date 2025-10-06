from fastapi import FastAPI
from .routes import projects, plan, nodes
from .database import init_db


from fastapi import FastAPI
from .routes import projects, plan, nodes
from .database import init_db
from .config import settings   # ✅ Add this line

# ✅ Print environment variables on startup
print("\n🔧 Loaded Environment Configuration:")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"Redis URL: {settings.REDIS_URL}")
print(f"S3 Endpoint: {settings.S3_ENDPOINT}")
print(f"S3 Bucket: {settings.S3_BUCKET}")
print(f"OpenAI Key: {'✅ Present' if settings.OPENAI_API_KEY else '❌ Not Provided'}\n")

app = FastAPI(title="Lucid Core")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(projects.router)
app.include_router(plan.router)
app.include_router(nodes.router)

@app.get("/health")
def health():
    return {"status": "ok"}
