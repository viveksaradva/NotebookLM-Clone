from backend.db.database import engine
from backend.db.models import Base, User, Document, Highlight, ChatSession, ChatMessage

def init_db():
    print("Creating database tables...")
    # Drop all tables first to ensure a clean slate
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    # List all tables that were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Created tables: {tables}")

if __name__ == "__main__":
    init_db()
