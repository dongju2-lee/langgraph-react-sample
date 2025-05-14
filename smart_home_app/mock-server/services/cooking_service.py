from models.cooking import (
    FoodRecommendationResponse, Recipe, RecipeStep, ResultResponse
)
from typing import List
from logging_config import setup_logger
import random

# 로거 설정
logger = setup_logger("cooking_service")

# 추천 음식 목록
FOOD_RECOMMENDATIONS = [
    "라자냐", "고구마튀김", "오징어볶음", "소고기 볶음밥", "닭볶음탕"
]

# 레시피 데이터
RECIPES = {
    "라자냐": Recipe(
        food_name="라자냐",
        ingredients=["소고기", "양파", "치즈", "토마토 소스", "라자냐 면"],
        steps=[
            RecipeStep(step_number=1, description="양파를 잘게 다져서 볶아주세요."),
            RecipeStep(step_number=2, description="소고기를 넣고 익힐 때까지 볶아주세요."),
            RecipeStep(step_number=3, description="토마토 소스를 넣고 끓여주세요."),
            RecipeStep(step_number=4, description="라자냐 면과 소스, 치즈를 층층이 쌓아주세요."),
            RecipeStep(step_number=5, description="180도 오븐에서 30분간 구워주세요.")
        ],
        required_appliances=["인덕션"]
    ),
    "고구마튀김": Recipe(
        food_name="고구마튀김",
        ingredients=["고구마", "튀김가루", "식용유"],
        steps=[
            RecipeStep(step_number=1, description="고구마를 깨끗이 씻고 껍질을 벗겨주세요."),
            RecipeStep(step_number=2, description="고구마를 적당한 크기로 자르고 튀김가루를 입혀주세요."),
            RecipeStep(step_number=3, description="인덕션에 식용유를 두르고 고구마를 바삭하게 튀겨주세요.")
        ],
        required_appliances=["인덕션"]
    ),
    "오징어볶음": Recipe(
        food_name="오징어볶음",
        ingredients=["오징어", "양파", "고추장", "설탕", "참기름"],
        steps=[
            RecipeStep(step_number=1, description="오징어를 깨끗이 손질하고 적당한 크기로 자르세요."),
            RecipeStep(step_number=2, description="양파를 채 썰고 고추장 양념을 만들어주세요."),
            RecipeStep(step_number=3, description="인덕션에 참기름을 두르고 양파를 볶다가 오징어를 넣고 볶아주세요."),
            RecipeStep(step_number=4, description="고추장 양념을 넣고 간을 맞춰 볶아주세요.")
        ],
        required_appliances=["인덕션"]
    ),
    "소고기 볶음밥": Recipe(
        food_name="소고기 볶음밥",
        ingredients=["소고기", "양파", "계란", "밥", "간장"],
        steps=[
            RecipeStep(step_number=1, description="소고기를 잘게 다져서 양념해주세요."),
            RecipeStep(step_number=2, description="인덕션에 기름을 두르고 소고기를 볶아주세요."),
            RecipeStep(step_number=3, description="양파를 넣고 같이 볶아주세요."),
            RecipeStep(step_number=4, description="밥을 넣고 간장을 넣어 볶아주세요."),
            RecipeStep(step_number=5, description="계란 프라이를 올려주세요.")
        ],
        required_appliances=["인덕션"]
    ),
    "닭볶음탕": Recipe(
        food_name="닭볶음탕",
        ingredients=["생닭", "양파", "감자", "당근", "고추장"],
        steps=[
            RecipeStep(step_number=1, description="닭을 깨끗이 손질하고 적당한 크기로 잘라주세요."),
            RecipeStep(step_number=2, description="야채들을 손질해서 큼직하게 잘라주세요."),
            RecipeStep(step_number=3, description="고추장 양념을 만들어주세요."),
            RecipeStep(step_number=4, description="인덕션에 닭을 먼저 볶다가 양념과 야채를 넣고 조려주세요.")
        ],
        required_appliances=["인덕션"]
    )
}

def recommend_food(ingredients: List[str]):
    """식재료 리스트로 요리 추천"""
    logger.info(f"서비스 호출: 식재료로 요리 추천 (재료: {ingredients})")
    # 랜덤으로 음식 추천 (실제로는 주어진 식재료를 기반으로 추천 로직 구현)
    recommended_food = random.choice(FOOD_RECOMMENDATIONS)
    return FoodRecommendationResponse(food_name=recommended_food)

def get_recipe(food_name: str):
    """음식 이름으로 레시피 조회"""
    logger.info(f"서비스 호출: 음식 레시피 조회 (음식: {food_name})")
    if food_name in RECIPES:
        return RECIPES[food_name]
    else:
        # 요청한 레시피가 없는 경우 임의의 레시피 반환
        logger.warning(f"요청한 레시피 '{food_name}'를 찾을 수 없습니다. 임의의 레시피를 반환합니다.")
        return random.choice(list(RECIPES.values())) 