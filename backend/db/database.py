from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Directly use SQLite instead of loading from settings
DATABASE_URL = "sqlite:///./documind.db"

# Create SQLAlchemy engine with SQLite-specific configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
