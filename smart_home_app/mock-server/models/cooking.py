from typing import List, Optional
from pydantic import BaseModel

class FoodRecommendationRequest(BaseModel):
    """음식 추천 요청 모델"""
    ingredients: List[str]

class FoodRecommendationResponse(BaseModel):
    """음식 추천 응답 모델"""
    food_name: str

# API에서 사용하는 FoodRecommendation 모델 추가
class FoodRecommendation(BaseModel):
    """음식 추천 모델"""
    food_name: str
    suitable_ingredients: List[str]

# API에서 사용하는 CookingIngredient 모델 추가
class CookingIngredient(BaseModel):
    """요리 재료 모델"""
    name: str
    quantity: str

# API에서는 CookingStep으로 사용하고 있음
class CookingStep(BaseModel):
    """요리 단계 모델"""
    step_number: int
    description: str

class RecipeRequest(BaseModel):
    """레시피 요청 모델"""
    food_name: str

class RecipeStep(BaseModel):
    """레시피 단계 모델"""
    step_number: int
    description: str

class Recipe(BaseModel):
    """레시피 모델"""
    name: str
    ingredients: List[CookingIngredient]
    steps: List[CookingStep]
    required_appliances: List[str]

class ResultResponse(BaseModel):
    """결과 응답 모델"""
    result: str
    message: Optional[str] = None