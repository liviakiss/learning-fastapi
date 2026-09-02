# main.py — FastAPI Day 2-3: Routes & Requests
# GET/POST/PUT/DELETE, path/query params, request bodies with Pydantic, error handling

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# --- Day 1 endpoints (kept for reference) ---
@app.get("/")
def read_root():
    return {"message": "Hello Lívia"}

@app.get("/greet/{name}")
def greet(name):
    return {"greeting": f"Hello {name}"}

@app.get("/double/{number}")
def double(number: int):
    return {"result": number * 2}

# --- Query parameters ---
@app.get("/search")
def search(query: str):
    return {"query": query}

# Default value = optional query param
@app.get("/paginate")
def paginate(page: int = 1):
    return {"page": page}

# --- Pydantic model: real runtime validation, not just compile-time typing ---
class Recipe(BaseModel):
    name: str
    servings: int
    ingredients: list[str]

# In-memory storage — resets on every server restart, temporary until Week 7's database
recipes_db = []

# POST — create
@app.post("/recipes")
def create_recipe(recipe: Recipe):
    recipe_id = len(recipes_db)
    recipes_db.append(recipe)
    return {"id": recipe_id, "recipe": recipe}

# GET — read one, with proper 404 handling (fixes the IndexError bug hit live)
@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    if recipe_id >= len(recipes_db) or recipe_id < 0:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipes_db[recipe_id]

# PUT — full update (requires the entire object, not partial)
@app.put("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, recipe: Recipe):
    if recipe_id >= len(recipes_db) or recipe_id < 0:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipes_db[recipe_id] = recipe
    return {"id": recipe_id, "updated": recipe}

# DELETE — remove
@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    if recipe_id >= len(recipes_db) or recipe_id < 0:
        raise HTTPException(status_code=404, detail="Recipe not found")
    deleted = recipes_db.pop(recipe_id)
    return {"deleted": deleted}