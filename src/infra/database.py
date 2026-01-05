from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import Config

# Create engine
# pool_recycle is important for MySQL to prevent connection timeout issues
engine = create_engine(
    Config.DATABASE_URL, 
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    # Import models here to ensure they are registered with Base
    from src.models.job import JobModel
    from src.models.candidate import CandidateModel
    Base.metadata.create_all(bind=engine)
