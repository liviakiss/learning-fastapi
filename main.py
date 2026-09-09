# main.py — FastAPI: Data Validation Deep Dive
# Optional fields, Field() constraints, response models

from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from recipe_helper import router as recipe_router
from sqlalchemy.orm import Session
from database import get_db
from models import RecipeDB

app = FastAPI()  # must come BEFORE include_router
app.include_router(recipe_router)

# --- Day 1 endpoints ---
@app.get("/")
def read_root():
    return {"message": "Hello Lívia"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"greeting": f"Hello {name}"}

@app.get("/double/{number}")
def double(number: int):
    return {"result": number * 2}

# --- Day 2: query parameters ---
@app.get("/search")
def search(query: str):
    return {"query": query}

@app.get("/paginate")
def paginate(page: int = 1):
    return {"page": page}

# --- Day 3: Pydantic model with constraints + optional field ---
class Recipe(BaseModel):
    name: str
    servings: int = Field(gt=0)              # value constraint: must be positive
    ingredients: list[str] = Field(min_length=1)  # value constraint: at least 1 item
    description: Optional[str] = None        # genuinely optional — type + default together

recipes_db = []

@app.post("/db-recipes")
def create_db_recipe(recipe: Recipe, db: Session = Depends(get_db)):
    new_recipe = RecipeDB(name=recipe.name, servings=recipe.servings)
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe

# response_model=Recipe: filters the output to ONLY these fields,
# even if the function's actual return value has extra data
@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    if recipe_id >= len(recipes_db) or recipe_id < 0:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe = recipes_db[recipe_id]
    data = recipe.model_dump()
    data["internal_flag"] = "do not expose this"  # simulates internal-only data
    return data  # response_model strips this before it reaches the client

@app.put("/db-recipes/{recipe_id}")
def update_db_recipe(recipe_id: int, recipe: Recipe, db: Session = Depends(get_db)):
    db_recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db_recipe.name = recipe.name
    db_recipe.servings = recipe.servings
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@app.delete("/db-recipes/{recipe_id}")
def delete_db_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(db_recipe)
    db.commit()
    return {"deleted": db_recipe.name}

@app.get("/db-recipes")
def get_all_recipes(db: Session = Depends(get_db)):
    recipes = db.query(RecipeDB).all()
    return recipes