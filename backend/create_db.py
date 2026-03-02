from db.session import engine
from db.base import Base
from db import model

Base.metadata.create_all(bind=engine)
print("Database created.")
