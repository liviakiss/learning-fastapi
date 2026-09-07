from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

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