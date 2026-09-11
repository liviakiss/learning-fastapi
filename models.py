# models.py — SQLAlchemy table models
from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class RecipeDB(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    servings = Column(Integer, nullable=False)

class ReviewDB(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    comment = Column(String)

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    intolerances_json = Column(String, nullable=True)  # small, fixed set -> JSON blob is fine

class FavoriteDB(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # open-ended, growable -> real table
    recipe_name = Column(String, nullable=False)