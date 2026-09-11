# recipe_helper.py — FastAPI: Recipe Helper API (the real project)

import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import UserDB, FavoriteDB

router = APIRouter()

# --- POST /recipe: ingredient analysis ---
class RecipeAnalysisRequest(BaseModel):
    ingredients: list[str]
    intolerances: list[str]

intolerance_keywords = {
    "gluten": ["flour", "wheat", "bread", "pasta"],
    "dairy": ["milk", "butter", "cheese", "cream"],
    "nuts": ["almond", "peanut", "walnut", "cashew"],
    "egg": ["egg"],
}

@router.post("/recipe")
def analyze_recipe(request: RecipeAnalysisRequest):
    flagged = []
    for ingredient in request.ingredients:
        lower_ingredient = ingredient.lower()
        for intolerance in request.intolerances:
            keywords = intolerance_keywords.get(intolerance, [])
            if any(word in lower_ingredient for word in keywords):
                flagged.append({"ingredient": ingredient, "reason": intolerance})
                break
    return {"flagged": flagged}

# --- GET /substitutes/{ingredient} ---
substitutes = {
    "milk": ["oat milk", "almond milk", "soy milk"],
    "butter": ["coconut oil", "vegan butter"],
    "wheat flour": ["almond flour", "rice flour", "oat flour"],
    "egg": ["mashed banana", "flax egg", "applesauce"],
}

@router.get("/substitutes/{ingredient}")
def get_substitutes(ingredient: str):
    options = substitutes.get(ingredient.lower())
    if options is None:
        raise HTTPException(status_code=404, detail="No substitutes found for this ingredient")
    return {"ingredient": ingredient, "substitutes": options}

# --- Per-user intolerances: JSON blob, identity from token not URL ---
class UserIntolerances(BaseModel):
    intolerances: list[str]

@router.post("/me/intolerances")
def set_my_intolerances(
    data: UserIntolerances,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(UserDB).filter(UserDB.username == current_user).first()
    user.intolerances_json = json.dumps(data.intolerances)  # real JSON, not a fragile comma-join
    db.commit()
    return {"username": current_user, "intolerances": data.intolerances}

@router.get("/me/intolerances")
def get_my_intolerances(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(UserDB).filter(UserDB.username == current_user).first()
    intolerances = json.loads(user.intolerances_json) if user.intolerances_json else []
    return {"username": current_user, "intolerances": intolerances}

# --- Favorites: real related table, open-ended + individually-manageable ---
class FavoriteCreate(BaseModel):
    recipe_name: str

@router.post("/me/favorites")
def add_favorite(
    data: FavoriteCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(UserDB).filter(UserDB.username == current_user).first()
    new_favorite = FavoriteDB(user_id=user.id, recipe_name=data.recipe_name)  # user.id, not current_user
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite

@router.get("/me/favorites")
def get_my_favorites(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(UserDB).filter(UserDB.username == current_user).first()
    favorites = db.query(FavoriteDB).filter(FavoriteDB.user_id == user.id).all()
    return favorites