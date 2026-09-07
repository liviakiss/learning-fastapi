# main.py — FastAPI: Data Validation Deep Dive
# Optional fields, Field() constraints, response models

from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from recipe_helper import router as recipe_router

app = FastAPI()
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

@app.post("/recipes")
def create_recipe(recipe: Recipe):
    recipe_id = len(recipes_db)
    recipes_db.append(recipe)
    return {"id": recipe_id, "recipe": recipe}

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

@app.put("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, recipe: Recipe):
    if recipe_id >= len(recipes_db) or recipe_id < 0:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipes_db[recipe_id] = recipe
    return {"id": recipe_id, "updated": recipe}

@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    if recipe_id >= len(recipes_db) or recipe_id < 0:
        raise HTTPException(status_code=404, detail="Recipe not found")
    deleted = recipes_db.pop(recipe_id)
    return {"deleted": deleted}