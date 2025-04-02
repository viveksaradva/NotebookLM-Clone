from auth.database import engine
from auth import models

# Create tables in the database
models.Base.metadata.create_all(bind=engine)

