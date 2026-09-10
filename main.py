# main.py — FastAPI Learning Log
# Day 1: first endpoints, decorators, path parameters
# Day 2: query parameters, Pydantic bodies, full CRUD, error handling
# Day 3: optional fields, Field constraints, response models
# project: see recipe_helper.py (via APIRouter)
# Database: SQLAlchemy models, real persistent CRUD
# Auth: password hashing, register/login, JWT, protected routes

from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from recipe_helper import router as recipe_router
from database import get_db
from models import RecipeDB, UserDB
from auth import hash_password, verify_password, create_access_token, get_current_user

app = FastAPI()  # must come BEFORE include_router
app.include_router(recipe_router)

# ============================================
# Day 1 — first endpoints
# ============================================
@app.get("/")
def read_root():
    return {"message": "Hello Lívia"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"greeting": f"Hello {name}"}

@app.get("/double/{number}")
def double(number: int):
    return {"result": number * 2}

# ============================================
# Day 2 — query parameters
# ============================================
@app.get("/search")
def search(query: str):
    return {"query": query}

@app.get("/paginate")
def paginate(page: int = 1):
    return {"page": page}

# ============================================
# Day 3 — Pydantic models
# ============================================
class Recipe(BaseModel):
    name: str
    servings: int = Field(gt=0)                    # value constraint: must be positive
    ingredients: list[str] = Field(min_length=1)    # value constraint: at least 1 item
    description: Optional[str] = None               # genuinely optional — type + default together

# ============================================
# Database Day 4 — real, persistent CRUD via SQLAlchemy
# Replaces the old in-memory recipes_db list entirely
# ============================================
@app.get("/db-recipes")
def get_all_recipes(db: Session = Depends(get_db)):
    return db.query(RecipeDB).all()

@app.post("/db-recipes")
def create_db_recipe(recipe: Recipe, db: Session = Depends(get_db)):
    new_recipe = RecipeDB(name=recipe.name, servings=recipe.servings)
    db.add(new_recipe)       # stages the change — NOT saved yet
    db.commit()               # actually writes it to disk permanently
    db.refresh(new_recipe)    # pulls the real auto-generated id back into the object
    return new_recipe

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

# ============================================
# Auth Day 5-6 — password hashing, register/login, JWT, protected routes
# ============================================
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = UserDB(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == credentials.username).first()
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def read_current_user(current_user: str = Depends(get_current_user)):
    return {"username": current_user}