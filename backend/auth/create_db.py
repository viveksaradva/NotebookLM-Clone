from backend.auth.database import engine
from backend.auth import models

# Create tables in the database
models.Base.metadata.create_all(bind=engine)

