# recipe_helper.py — FastAPI: Recipe Helper API
# Organized separately from main.py via APIRouter — this is the real project

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
            keywords = intolerance_keywords.get(intolerance, [])  # safe lookup, avoids KeyError
            if any(word in lower_ingredient for word in keywords):  # Python's .some()
                flagged.append({"ingredient": ingredient, "reason": intolerance})
                break
    return {"flagged": flagged}

# --- GET /substitutes/{ingredient}: lookup with 404 fallback ---
substitutes = {
    "milk": ["oat milk", "almond milk", "soy milk"],
    "butter": ["coconut oil", "vegan butter"],
    "wheat flour": ["almond flour", "rice flour", "oat flour"],
    "egg": ["mashed banana", "flax egg", "applesauce"],
}

@router.get("/substitutes/{ingredient}")
def get_substitutes(ingredient: str):
    options = substitutes.get(ingredient.lower())  # no default -> None if missing
    if options is None:
        raise HTTPException(status_code=404, detail="No substitutes found for this ingredient")
    return {"ingredient": ingredient, "substitutes": options}

# --- Per-user intolerance storage (in-memory, temporary until database) ---
class UserIntolerances(BaseModel):
    intolerances: list[str]

user_intolerances_db: dict[str, list[str]] = {}

@router.post("/users/{user_id}/intolerances")
def set_user_intolerances(user_id: str, data: UserIntolerances):
    user_intolerances_db[user_id] = data.intolerances
    return {"user_id": user_id, "intolerances": data.intolerances}

@router.get("/users/{user_id}/intolerances")
def get_user_intolerances(user_id: str):
    intolerances = user_intolerances_db.get(user_id)
    if intolerances is None:
        raise HTTPException(status_code=404, detail="No intolerances found for this user")
    return {"user_id": user_id, "intolerances": intolerances}