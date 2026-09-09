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