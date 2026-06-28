"""
Module 2: AI Dietician & Calorie Coach
NLP-driven diet recommendations based on BMI, goals, and preferences.
Generates grocery lists and tracks nutritional intake.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import math

router = APIRouter()


# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────
class UserProfile(BaseModel):
    name: str
    age: int
    gender: str                  # "male" / "female"
    height_cm: float
    weight_kg: float
    goal: str                    # "lose_weight" / "gain_muscle" / "maintain"
    activity_level: str          # "sedentary" / "light" / "moderate" / "active" / "very_active"
    dietary_preference: str      # "vegetarian" / "vegan" / "non-vegetarian" / "keto"
    allergies: Optional[List[str]] = []

class MealLog(BaseModel):
    meal_name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


# ──────────────────────────────────────────────
# Nutrition Data
# ──────────────────────────────────────────────
ACTIVITY_MULTIPLIERS = {
    "sedentary":    1.2,
    "light":        1.375,
    "moderate":     1.55,
    "active":       1.725,
    "very_active":  1.9
}

MEAL_DATABASE = {
    "vegetarian": {
        "breakfast": [
            {"name": "Oats with banana & almonds",      "cal": 380, "protein": 14, "carbs": 58, "fat": 10},
            {"name": "Paneer scramble with toast",      "cal": 420, "protein": 22, "carbs": 35, "fat": 18},
            {"name": "Greek yogurt parfait",            "cal": 310, "protein": 18, "carbs": 40, "fat": 8},
        ],
        "lunch": [
            {"name": "Dal rice with salad",             "cal": 520, "protein": 20, "carbs": 80, "fat": 10},
            {"name": "Rajma with brown rice",           "cal": 560, "protein": 24, "carbs": 85, "fat": 8},
            {"name": "Vegetable khichdi",               "cal": 450, "protein": 18, "carbs": 70, "fat": 10},
        ],
        "dinner": [
            {"name": "Paneer tikka with roti",          "cal": 490, "protein": 28, "carbs": 45, "fat": 20},
            {"name": "Mixed vegetable curry with rice", "cal": 430, "protein": 15, "carbs": 68, "fat": 12},
            {"name": "Tofu stir fry with quinoa",       "cal": 410, "protein": 24, "carbs": 48, "fat": 14},
        ],
        "snacks": [
            {"name": "Mixed nuts (30g)",                "cal": 180, "protein": 5,  "carbs": 8,  "fat": 15},
            {"name": "Hummus with carrot sticks",       "cal": 150, "protein": 6,  "carbs": 18, "fat": 7},
            {"name": "Fruit salad",                     "cal": 120, "protein": 2,  "carbs": 28, "fat": 1},
        ]
    },
    "non-vegetarian": {
        "breakfast": [
            {"name": "Eggs (3) with whole wheat toast", "cal": 390, "protein": 26, "carbs": 30, "fat": 18},
            {"name": "Chicken omelette",                "cal": 350, "protein": 30, "carbs": 12, "fat": 18},
            {"name": "Oats with whey protein",          "cal": 400, "protein": 30, "carbs": 52, "fat": 8},
        ],
        "lunch": [
            {"name": "Grilled chicken with brown rice", "cal": 550, "protein": 45, "carbs": 55, "fat": 12},
            {"name": "Tuna salad wrap",                 "cal": 420, "protein": 35, "carbs": 38, "fat": 14},
            {"name": "Egg curry with roti",             "cal": 500, "protein": 28, "carbs": 48, "fat": 18},
        ],
        "dinner": [
            {"name": "Grilled salmon with veggies",     "cal": 480, "protein": 40, "carbs": 25, "fat": 22},
            {"name": "Chicken stir fry with rice",      "cal": 520, "protein": 42, "carbs": 50, "fat": 14},
            {"name": "Fish curry with brown rice",      "cal": 490, "protein": 38, "carbs": 52, "fat": 15},
        ],
        "snacks": [
            {"name": "Boiled eggs (2)",                 "cal": 140, "protein": 12, "carbs": 1,  "fat": 10},
            {"name": "Greek yogurt",                    "cal": 130, "protein": 15, "carbs": 8,  "fat": 4},
            {"name": "Chicken jerky (30g)",             "cal": 100, "protein": 18, "carbs": 2,  "fat": 2},
        ]
    },
    "vegan": {
        "breakfast": [
            {"name": "Chia pudding with berries",       "cal": 320, "protein": 12, "carbs": 42, "fat": 12},
            {"name": "Smoothie bowl (banana, spinach)", "cal": 360, "protein": 10, "carbs": 65, "fat": 8},
            {"name": "Peanut butter oat bars",          "cal": 380, "protein": 14, "carbs": 52, "fat": 15},
        ],
        "lunch": [
            {"name": "Lentil soup with bread",          "cal": 480, "protein": 22, "carbs": 72, "fat": 8},
            {"name": "Chickpea salad bowl",             "cal": 420, "protein": 18, "carbs": 58, "fat": 12},
            {"name": "Tofu Buddha bowl",                "cal": 460, "protein": 24, "carbs": 55, "fat": 16},
        ],
        "dinner": [
            {"name": "Tempeh curry with quinoa",        "cal": 500, "protein": 28, "carbs": 60, "fat": 14},
            {"name": "Black bean tacos",                "cal": 440, "protein": 20, "carbs": 62, "fat": 12},
            {"name": "Vegan stir fry with noodles",     "cal": 420, "protein": 16, "carbs": 65, "fat": 12},
        ],
        "snacks": [
            {"name": "Edamame (half cup)",              "cal": 120, "protein": 11, "carbs": 10, "fat": 5},
            {"name": "Trail mix (30g)",                 "cal": 170, "protein": 5,  "carbs": 18, "fat": 10},
            {"name": "Apple with almond butter",        "cal": 200, "protein": 4,  "carbs": 28, "fat": 10},
        ]
    },
    "keto": {
        "breakfast": [
            {"name": "Avocado egg cups",                "cal": 380, "protein": 18, "carbs": 4,  "fat": 32},
            {"name": "Bacon & cheese omelette",         "cal": 420, "protein": 24, "carbs": 2,  "fat": 36},
            {"name": "Keto smoothie (MCT, coconut)",    "cal": 350, "protein": 15, "carbs": 5,  "fat": 30},
        ],
        "lunch": [
            {"name": "Grilled chicken Caesar (no croutons)", "cal": 480, "protein": 42, "carbs": 6, "fat": 30},
            {"name": "Tuna lettuce wraps",              "cal": 350, "protein": 35, "carbs": 4,  "fat": 22},
            {"name": "Zucchini noodles with pesto",     "cal": 400, "protein": 18, "carbs": 8,  "fat": 34},
        ],
        "dinner": [
            {"name": "Ribeye steak with asparagus",     "cal": 600, "protein": 48, "carbs": 6,  "fat": 42},
            {"name": "Salmon with broccoli & butter",   "cal": 520, "protein": 40, "carbs": 8,  "fat": 38},
            {"name": "Lamb chops with spinach",         "cal": 560, "protein": 45, "carbs": 5,  "fat": 40},
        ],
        "snacks": [
            {"name": "Cheese cubes (30g)",              "cal": 120, "protein": 7,  "carbs": 1,  "fat": 10},
            {"name": "Macadamia nuts (20g)",            "cal": 140, "protein": 2,  "carbs": 2,  "fat": 15},
            {"name": "Beef jerky (30g)",                "cal": 100, "protein": 16, "carbs": 2,  "fat": 3},
        ]
    }
}


# ──────────────────────────────────────────────
# Core functions
# ──────────────────────────────────────────────
def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return {"bmi": bmi, "category": category}


def calculate_tdee(profile: UserProfile) -> int:
    """Harris-Benedict BMR × activity multiplier."""
    if profile.gender.lower() == "male":
        bmr = 88.362 + (13.397 * profile.weight_kg) + (4.799 * profile.height_cm) - (5.677 * profile.age)
    else:
        bmr = 447.593 + (9.247 * profile.weight_kg) + (3.098 * profile.height_cm) - (4.330 * profile.age)

    multiplier = ACTIVITY_MULTIPLIERS.get(profile.activity_level, 1.55)
    tdee = bmr * multiplier

    if profile.goal == "lose_weight":
        tdee -= 500    # 500 kcal deficit
    elif profile.goal == "gain_muscle":
        tdee += 300    # 300 kcal surplus

    return int(tdee)


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@router.post("/diet-plan")
def generate_diet_plan(profile: UserProfile):
    """Generate a full daily diet plan based on user profile."""
    bmi_data    = calculate_bmi(profile.weight_kg, profile.height_cm)
    daily_cals  = calculate_tdee(profile)
    pref        = profile.dietary_preference.lower()

    if pref not in MEAL_DATABASE:
        pref = "non-vegetarian"

    meals = MEAL_DATABASE[pref]

    # Macro targets (protein: 30%, carbs: 40%, fat: 30% for balanced)
    protein_target = round((daily_cals * 0.30) / 4, 0)
    carbs_target   = round((daily_cals * 0.40) / 4, 0)
    fat_target     = round((daily_cals * 0.30) / 9, 0)

    if profile.goal == "gain_muscle":
        protein_target = round(profile.weight_kg * 2.0, 0)   # 2g per kg

    plan = {
        "breakfast": meals["breakfast"][0],
        "mid_morning_snack": meals["snacks"][0],
        "lunch": meals["lunch"][0],
        "evening_snack": meals["snacks"][1],
        "dinner": meals["dinner"][0],
    }

    total_cals = sum(m["cal"] for m in plan.values())

    return {
        "user": profile.name,
        "bmi": bmi_data,
        "goal": profile.goal,
        "daily_calorie_target": daily_cals,
        "macro_targets": {
            "protein_g": protein_target,
            "carbs_g":   carbs_target,
            "fat_g":     fat_target
        },
        "meal_plan": plan,
        "estimated_total_calories": total_cals,
        "hydration_goal_liters": round(profile.weight_kg * 0.033, 1),
        "notes": [
            f"Your BMI is {bmi_data['bmi']} ({bmi_data['category']})",
            f"Daily target: {daily_cals} kcal",
            "Eat every 3–4 hours to maintain metabolism",
            "Drink water before each meal"
        ]
    }


@router.post("/grocery-list")
def generate_grocery_list(profile: UserProfile):
    """Generate a weekly grocery list based on diet preference."""
    pref = profile.dietary_preference.lower()

    grocery = {
        "vegetarian": {
            "proteins":  ["Paneer (500g)", "Greek yogurt (1kg)", "Tofu (400g)", "Eggs (1 dozen)", "Mixed lentils (1kg)", "Chickpeas (500g)"],
            "grains":    ["Brown rice (2kg)", "Oats (1kg)", "Whole wheat flour (1kg)", "Quinoa (500g)"],
            "vegetables":["Spinach", "Broccoli", "Carrots", "Tomatoes", "Capsicum", "Zucchini", "Cucumber"],
            "fruits":    ["Bananas (1 dozen)", "Apples (6)", "Berries (500g)", "Oranges (6)"],
            "fats":      ["Almonds (250g)", "Walnuts (200g)", "Olive oil (500ml)", "Almond butter"]
        },
        "non-vegetarian": {
            "proteins":  ["Chicken breast (1kg)", "Eggs (2 dozen)", "Salmon fillets (500g)", "Tuna cans (4)", "Greek yogurt (500g)"],
            "grains":    ["Brown rice (2kg)", "Oats (500g)", "Whole wheat bread"],
            "vegetables":["Broccoli", "Spinach", "Asparagus", "Bell peppers", "Zucchini"],
            "fruits":    ["Bananas (1 dozen)", "Apples (6)", "Berries (500g)"],
            "fats":      ["Olive oil (500ml)", "Avocados (4)", "Mixed nuts (250g)"]
        },
        "vegan": {
            "proteins":  ["Tofu (600g)", "Tempeh (400g)", "Lentils (1kg)", "Chickpeas (1kg)", "Black beans (500g)", "Edamame (500g)"],
            "grains":    ["Quinoa (1kg)", "Brown rice (2kg)", "Oats (1kg)"],
            "vegetables":["All leafy greens", "Sweet potato", "Broccoli", "Zucchini", "Mushrooms"],
            "fruits":    ["Bananas (2 dozen)", "Mixed berries (1kg)", "Dates (200g)", "Avocados (6)"],
            "fats":      ["Coconut oil", "Almond butter", "Flaxseeds", "Chia seeds", "Hemp seeds"]
        },
        "keto": {
            "proteins":  ["Chicken thighs (1kg)", "Salmon (500g)", "Eggs (3 dozen)", "Ground beef (500g)", "Bacon (300g)"],
            "fats":      ["Avocados (8)", "Butter (250g)", "MCT oil", "Olive oil (500ml)", "Cheese (500g)", "Heavy cream"],
            "vegetables":["Spinach", "Kale", "Zucchini", "Cauliflower", "Broccoli", "Asparagus"],
            "nuts":      ["Macadamia nuts (200g)", "Walnuts (200g)", "Almonds (200g)"],
            "misc":      ["Coconut flour", "Almond flour", "Erythritol (sweetener)"]
        }
    }

    return {
        "dietary_preference": pref,
        "weekly_grocery_list": grocery.get(pref, grocery["non-vegetarian"]),
        "tip": "Meal prep on Sundays to stay consistent throughout the week!"
    }


@router.post("/track-meal")
def track_meal(log: MealLog):
    """Log a meal and get nutritional feedback."""
    feedback = []
    if log.protein_g < 20:
        feedback.append("⚠️ Low protein — consider adding a protein source")
    if log.calories > 700:
        feedback.append("⚠️ High-calorie meal — balance with lighter meals today")
    if log.fat_g > 40:
        feedback.append("⚠️ High fat content — opt for healthier fat sources")
    if not feedback:
        feedback.append("✅ Well-balanced meal!")

    return {
        "meal": log.meal_name,
        "nutrition": {
            "calories": log.calories,
            "protein_g": log.protein_g,
            "carbs_g":   log.carbs_g,
            "fat_g":     log.fat_g
        },
        "feedback": feedback,
        "macro_split_percent": {
            "protein": round((log.protein_g * 4 / log.calories) * 100, 1) if log.calories > 0 else 0,
            "carbs":   round((log.carbs_g * 4 / log.calories) * 100, 1)   if log.calories > 0 else 0,
            "fat":     round((log.fat_g * 9 / log.calories) * 100, 1)     if log.calories > 0 else 0,
        }
    }
