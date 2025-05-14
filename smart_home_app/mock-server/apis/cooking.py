from fastapi import APIRouter, HTTPException, Body
from typing import List
from models.cooking import Recipe, FoodRecommendation, CookingIngredient, CookingStep
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("cooking_api")

router = APIRouter(
    prefix="/api/cooking",
    tags=["cooking"],
    responses={404: {"description": "페이지를 찾을 수 없습니다."}},
)

# 샘플 레시피 데이터
recipes = {
    "라자냐": Recipe(
        name="라자냐",
        ingredients=[
            CookingIngredient(name="라자냐 면", quantity="1팩"),
            CookingIngredient(name="소고기", quantity="200g"),
            CookingIngredient(name="토마토 소스", quantity="1컵"),
            CookingIngredient(name="치즈", quantity="2컵")
        ],
        steps=[
            CookingStep(step_number=1, description="소고기를 볶습니다."),
            CookingStep(step_number=2, description="토마토 소스를 붓고 조리합니다."),
            CookingStep(step_number=3, description="라자냐 면과 소스를 겹겹이 쌓습니다."),
            CookingStep(step_number=4, description="치즈를 올리고 오븐에 굽습니다.")
        ],
        required_appliances=["인덕션", "오븐"]
    ),
    "고구마튀김": Recipe(
        name="고구마튀김",
        ingredients=[
            CookingIngredient(name="고구마", quantity="2개"),
            CookingIngredient(name="식용유", quantity="적당량"),
            CookingIngredient(name="설탕", quantity="약간")
        ],
        steps=[
            CookingStep(step_number=1, description="고구마를 깨끗이 씻고 껍질을 벗깁니다."),
            CookingStep(step_number=2, description="고구마를 먹기 좋은 크기로 자릅니다."),
            CookingStep(step_number=3, description="인덕션에 기름을 두르고 고구마를 노릇하게 튀깁니다."),
            CookingStep(step_number=4, description="설탕을 약간 뿌려 맛을 더합니다.")
        ],
        required_appliances=["인덕션"]
    ),
    "오징어볶음": Recipe(
        name="오징어볶음",
        ingredients=[
            CookingIngredient(name="오징어", quantity="2마리"),
            CookingIngredient(name="고추장", quantity="2큰술"),
            CookingIngredient(name="양파", quantity="1개"),
            CookingIngredient(name="당근", quantity="1/2개")
        ],
        steps=[
            CookingStep(step_number=1, description="오징어를 깨끗이 손질하고 적당한 크기로 자릅니다."),
            CookingStep(step_number=2, description="양파와 당근을 채 썹니다."),
            CookingStep(step_number=3, description="인덕션에 기름을 두르고 채소를 볶습니다."),
            CookingStep(step_number=4, description="오징어를 넣고 고추장과 함께 볶습니다.")
        ],
        required_appliances=["인덕션"]
    ),
    "소고기 볶음밥": Recipe(
        name="소고기 볶음밥",
        ingredients=[
            CookingIngredient(name="소고기", quantity="100g"),
            CookingIngredient(name="밥", quantity="1공기"),
            CookingIngredient(name="양파", quantity="1/2개"),
            CookingIngredient(name="당근", quantity="1/4개"),
            CookingIngredient(name="계란", quantity="1개")
        ],
        steps=[
            CookingStep(step_number=1, description="소고기와 채소를 잘게 썹니다."),
            CookingStep(step_number=2, description="인덕션에 기름을 두르고 소고기를 볶습니다."),
            CookingStep(step_number=3, description="채소를 넣고 함께 볶습니다."),
            CookingStep(step_number=4, description="밥을 넣고 간장과 함께 볶습니다."),
            CookingStep(step_number=5, description="계란을 풀어 마무리합니다.")
        ],
        required_appliances=["인덕션"]
    ),
    "닭볶음탕": Recipe(
        name="닭볶음탕",
        ingredients=[
            CookingIngredient(name="생닭", quantity="1마리"),
            CookingIngredient(name="감자", quantity="2개"),
            CookingIngredient(name="당근", quantity="1개"),
            CookingIngredient(name="고추장", quantity="2큰술"),
            CookingIngredient(name="고춧가루", quantity="1큰술")
        ],
        steps=[
            CookingStep(step_number=1, description="닭을 깨끗이 씻고 적당한 크기로 자릅니다."),
            CookingStep(step_number=2, description="감자와 당근을 큼직하게 썹니다."),
            CookingStep(step_number=3, description="인덕션에 기름을 두르고 닭을 볶습니다."),
            CookingStep(step_number=4, description="양념을 넣고 물을 부어 끓입니다."),
            CookingStep(step_number=5, description="채소를 넣고 함께 끓입니다.")
        ],
        required_appliances=["인덕션"]
    )
}

# 재료에 따른 음식 추천 로직
ingredient_to_food_map = {
    "소고기": ["소고기 볶음밥", "라자냐"],
    "고구마": ["고구마튀김"],
    "오징어": ["오징어볶음"],
    "생닭": ["닭볶음탕"],
    "양파": ["소고기 볶음밥", "오징어볶음"],
    "치즈": ["라자냐"]
}

@router.post("/recommend", response_model=FoodRecommendation)
async def recommend_food(ingredients: List[str] = Body(...)):
    """식재료를 기반으로 요리를 추천합니다."""
    logger.info(f"API 호출: 식재료 기반 요리 추천 - 재료: {ingredients}")
    
    potential_foods = set()
    suitable_ingredients = []
    
    for ingredient in ingredients:
        if ingredient in ingredient_to_food_map:
            suitable_ingredients.append(ingredient)
            for food in ingredient_to_food_map[ingredient]:
                potential_foods.add(food)
    
    if not potential_foods:
        # 기본 추천
        recommended_food = "소고기 볶음밥"
    else:
        recommended_food = list(potential_foods)[0]
    
    return FoodRecommendation(
        food_name=recommended_food,
        suitable_ingredients=suitable_ingredients
    )

@router.get("/recipe/{food_name}", response_model=Recipe)
async def get_recipe(food_name: str):
    """음식 이름을 기반으로 레시피를 반환합니다."""
    logger.info(f"API 호출: 레시피 조회 - 음식: {food_name}")
    
    if food_name not in recipes:
        raise HTTPException(status_code=404, detail="해당 음식의 레시피를 찾을 수 없습니다.")
    
    return recipes[food_name] 