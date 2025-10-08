# ---------------------------------------------------------
# 🧱 Database Configuration — SQLAlchemy Setup
# ---------------------------------------------------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from Backend.app.config import settings

# ---------------------------------------------------------
# Database URL from Environment
# ---------------------------------------------------------
DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Create Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for Models
Base = declarative_base()


# ---------------------------------------------------------
# Database Dependency for FastAPI Routes
# ---------------------------------------------------------
def get_db():
    """
    FastAPI dependency that provides a database session
    and automatically closes it after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# Database Initialization Function
# ---------------------------------------------------------
def init_db():
    """
    Initializes database tables dynamically.
    Imports models lazily to avoid circular imports.
    """
    from Backend.app import models  # ✅ Lazy import prevents circular dependency
    print("🧩 Creating database tables (if not exist)...")
    Base.metadata.create_all(bind=engine)
