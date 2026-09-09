# database.py — engine, session factory, Base, and the get_db dependency
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("sqlite:///./recipes.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Generator + finally = same job as useEffect's cleanup function:
# hand out a resource, guarantee cleanup after it's used
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

