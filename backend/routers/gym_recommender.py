"""
Module 7: Gym Recommender & Planner
AI recommendation engine for gyms, workout programs, and fitness challenges
based on user goals, location, and historical data.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class UserPreference(BaseModel):
    user_id: str
    location: str               # city / area
    fitness_goal: str           # "weight_loss" / "muscle_gain" / "endurance" / "flexibility"
    fitness_level: str          # "beginner" / "intermediate" / "advanced"
    budget_inr: int             # monthly budget
    preferred_timing: str       # "morning" / "evening" / "flexible"
    equipment_preference: str   # "gym" / "home" / "outdoor" / "any"
    past_programs: Optional[List[str]] = []

class ProgramRequest(BaseModel):
    fitness_goal: str
    fitness_level: str
    days_per_week: int
    equipment: str              # "full_gym" / "home" / "minimal"


# ──────────────────────────────────────────────
# Data
# ──────────────────────────────────────────────
GYM_DATABASE = {
    "pune": [
        {"name": "Gold's Gym Hinjewadi",    "area": "Hinjewadi",  "monthly_fee": 1500, "rating": 4.5, "facilities": ["Pool", "Cardio Zone", "Weights", "Personal Training"], "timing": "5AM–10PM"},
        {"name": "Snap Fitness Baner",       "area": "Baner",      "monthly_fee": 1200, "rating": 4.2, "facilities": ["24/7 Access", "Cardio", "Weights"], "timing": "24/7"},
        {"name": "Cult.fit Kharadi",         "area": "Kharadi",    "monthly_fee": 2000, "rating": 4.6, "facilities": ["Group Classes", "Yoga", "HIIT", "Weights"], "timing": "6AM–9PM"},
        {"name": "Anytime Fitness Wakad",    "area": "Wakad",      "monthly_fee": 1800, "rating": 4.3, "facilities": ["24/7 Access", "Cardio", "Strength"], "timing": "24/7"},
        {"name": "Talwalkars Pimpri",        "area": "Pimpri",     "monthly_fee": 900,  "rating": 4.0, "facilities": ["Cardio", "Weights", "Steam Room"], "timing": "6AM–9PM"},
        {"name": "CrossFit Aundh",           "area": "Aundh",      "monthly_fee": 2500, "rating": 4.7, "facilities": ["CrossFit", "Olympic Lifting", "Coaching"], "timing": "6AM–8PM"},
    ],
    "mumbai": [
        {"name": "Gold's Gym Andheri",       "area": "Andheri",    "monthly_fee": 2000, "rating": 4.4, "facilities": ["Pool", "Cardio", "Weights", "Spa"], "timing": "6AM–10PM"},
        {"name": "Fitness First Bandra",     "area": "Bandra",     "monthly_fee": 3000, "rating": 4.6, "facilities": ["Premium Equipment", "Classes", "Nutrition Coaching"], "timing": "6AM–10PM"},
    ]
}

WORKOUT_PROGRAMS = {
    "weight_loss": {
        "beginner": {
            "name":        "Fat Burn Foundation — 8 Weeks",
            "description": "Low-impact cardio + full body resistance to kickstart fat loss",
            "schedule": [
                {"day": "Monday",    "focus": "Full Body Cardio",   "exercises": ["Brisk Walk 30 min", "Bodyweight Squats 3×15", "Push-ups 3×10", "Plank 3×30sec"]},
                {"day": "Wednesday", "focus": "Core + Cardio",      "exercises": ["Cycling 25 min", "Crunches 3×20", "Leg Raises 3×15", "Mountain Climbers 3×30sec"]},
                {"day": "Friday",    "focus": "Lower Body + Cardio","exercises": ["Treadmill 20 min", "Lunges 3×12", "Glute Bridges 3×15", "Step-ups 3×12"]},
            ],
            "nutrition_tip": "500 kcal deficit/day with high protein diet",
            "expected_result": "Lose 0.5–1 kg/week"
        },
        "intermediate": {
            "name":        "HIIT & Strength Hybrid — 10 Weeks",
            "description": "High-intensity intervals combined with strength training",
            "schedule": [
                {"day": "Monday",    "focus": "Upper Body + HIIT",  "exercises": ["Bench Press 4×10", "Rows 4×10", "Shoulder Press 3×12", "HIIT Sprints 15 min"]},
                {"day": "Tuesday",   "focus": "HIIT Cardio",        "exercises": ["Treadmill Intervals 25 min", "Battle Ropes 4×30sec", "Box Jumps 4×10"]},
                {"day": "Thursday",  "focus": "Lower Body",         "exercises": ["Squats 4×10", "Deadlifts 3×8", "Leg Press 3×12", "Calf Raises 4×20"]},
                {"day": "Saturday",  "focus": "Full Body Circuit",  "exercises": ["Burpees 3×15", "Kettlebell Swings 3×15", "Pull-ups 3×8", "Dips 3×12"]},
            ],
            "nutrition_tip": "400–500 kcal deficit, 1.8g protein/kg bodyweight",
            "expected_result": "Lose 0.75–1.25 kg/week"
        }
    },
    "muscle_gain": {
        "beginner": {
            "name":        "Strength Foundation — 12 Weeks",
            "description": "Progressive overload fundamentals to build muscle from scratch",
            "schedule": [
                {"day": "Monday",    "focus": "Push (Chest/Shoulders/Triceps)", "exercises": ["Bench Press 3×8", "Shoulder Press 3×10", "Tricep Pushdown 3×12", "Push-ups 3×15"]},
                {"day": "Wednesday", "focus": "Pull (Back/Biceps)",             "exercises": ["Lat Pulldown 3×10", "Seated Row 3×10", "Bicep Curls 3×12", "Face Pulls 3×15"]},
                {"day": "Friday",    "focus": "Legs",                           "exercises": ["Squats 3×8", "Leg Press 3×10", "Leg Curl 3×12", "Calf Raises 4×20"]},
            ],
            "nutrition_tip": "300 kcal surplus, 2.0–2.2g protein/kg bodyweight",
            "expected_result": "Gain 0.5–1 kg muscle/month"
        },
        "advanced": {
            "name":        "Hypertrophy Elite — PPL + Rest — 16 Weeks",
            "description": "Push-Pull-Legs 6 day split for maximum hypertrophy",
            "schedule": [
                {"day": "Monday",    "focus": "Push A", "exercises": ["Flat Bench 5×5", "Incline DB 4×8", "OHP 4×8", "Lateral Raises 4×15", "Tricep Pushdown 4×12"]},
                {"day": "Tuesday",   "focus": "Pull A", "exercises": ["Deadlift 4×5", "Pull-ups 4×8", "Cable Row 4×10", "Face Pulls 4×15", "Hammer Curls 3×12"]},
                {"day": "Wednesday", "focus": "Legs A", "exercises": ["Squat 5×5", "Romanian DL 4×8", "Leg Press 4×12", "Leg Curl 4×12", "Calf 5×20"]},
                {"day": "Thursday",  "focus": "Push B", "exercises": ["Incline Bench 4×8", "Cable Fly 4×12", "Arnold Press 4×10", "Skull Crushers 3×10"]},
                {"day": "Friday",    "focus": "Pull B", "exercises": ["Barbell Row 4×8", "Lat Pulldown 4×10", "Chest-Supported Row 4×10", "Preacher Curl 3×12"]},
                {"day": "Saturday",  "focus": "Legs B", "exercises": ["Front Squat 4×8", "Hack Squat 4×10", "Walking Lunges 3×12", "Nordic Curl 3×6"]},
            ],
            "nutrition_tip": "250 kcal surplus, 2.2g protein/kg, creatine 5g/day",
            "expected_result": "Gain 0.75–1.5 kg lean mass/month"
        }
    },
    "endurance": {
        "beginner": {
            "name":        "Run to Fitness — 8 Weeks",
            "description": "Couch to 5K style endurance building program",
            "schedule": [
                {"day": "Monday",    "focus": "Run/Walk Intervals", "exercises": ["5 min warm-up walk", "8× (1 min run + 1.5 min walk)", "5 min cool-down"]},
                {"day": "Wednesday", "focus": "Cross Training",     "exercises": ["Cycling 30 min", "Swimming 20 min (optional)", "Core Work 15 min"]},
                {"day": "Saturday",  "focus": "Long Run",           "exercises": ["Steady pace run 20–30 min", "Light stretching 10 min"]},
            ],
            "nutrition_tip": "Carb-forward diet for sustained energy",
            "expected_result": "Complete 5K run by week 8"
        }
    },
    "flexibility": {
        "beginner": {
            "name":        "Mobility & Flexibility — Ongoing",
            "description": "Daily mobility work for injury prevention and flexibility gains",
            "schedule": [
                {"day": "Daily",     "focus": "Morning Mobility",   "exercises": ["Cat-Cow 2×10", "Hip Circles 2×10", "Shoulder Rolls 2×10", "Thoracic Rotations 2×10"]},
                {"day": "Mon/Thu",   "focus": "Deep Stretch",       "exercises": ["Pigeon Pose 2 min/side", "Hamstring Stretch 2 min", "Hip Flexor Lunge 2 min", "Chest Opener 1 min"]},
                {"day": "Wed/Sat",   "focus": "Yoga Flow",          "exercises": ["Sun Salutation ×5", "Warrior I & II", "Downward Dog Flow", "Child's Pose"]},
            ],
            "nutrition_tip": "Anti-inflammatory foods: turmeric, berries, leafy greens",
            "expected_result": "Noticeable flexibility gains in 4–6 weeks"
        }
    }
}

CHALLENGES = [
    {"id": "c1", "name": "30-Day Squat Challenge",   "duration_days": 30, "goal": "muscle_gain",  "difficulty": "beginner",     "daily_target": "Progress from 50 to 250 squats"},
    {"id": "c2", "name": "21-Day HIIT Blast",        "duration_days": 21, "goal": "weight_loss",  "difficulty": "intermediate", "daily_target": "20 min HIIT every day"},
    {"id": "c3", "name": "10K Steps Daily — 2 Weeks","duration_days": 14, "goal": "endurance",    "difficulty": "beginner",     "daily_target": "Walk or run 10,000 steps"},
    {"id": "c4", "name": "100 Push-Up Challenge",    "duration_days": 30, "goal": "muscle_gain",  "difficulty": "intermediate", "daily_target": "Work up to 100 consecutive push-ups"},
    {"id": "c5", "name": "Yoga Flexibility Month",   "duration_days": 30, "goal": "flexibility",  "difficulty": "beginner",     "daily_target": "15 min yoga session daily"},
]


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@router.post("/recommend-gyms")
def recommend_gyms(pref: UserPreference):
    """Recommend nearby gyms based on location, budget, and goal."""
    city  = pref.location.lower()
    gyms  = GYM_DATABASE.get(city, GYM_DATABASE["pune"])   # Default to Pune

    filtered = [g for g in gyms if g["monthly_fee"] <= pref.budget_inr]
    if not filtered:
        filtered = sorted(gyms, key=lambda x: x["monthly_fee"])[:3]

    filtered = sorted(filtered, key=lambda x: x["rating"], reverse=True)

    return {
        "user_id":    pref.user_id,
        "location":   pref.location,
        "budget_inr": pref.budget_inr,
        "goal":       pref.fitness_goal,
        "top_picks":  filtered[:3],
        "tip":        "Visit during your preferred workout time to check crowd levels before joining!"
    }


@router.post("/recommend-program")
def recommend_program(req: ProgramRequest):
    """Recommend a workout program based on goal and fitness level."""
    goal  = req.fitness_goal.lower()
    level = req.fitness_level.lower()

    if goal not in WORKOUT_PROGRAMS:
        raise HTTPException(status_code=404, detail=f"Goal '{goal}' not found. Try: {list(WORKOUT_PROGRAMS.keys())}")

    level_programs = WORKOUT_PROGRAMS[goal]
    program = level_programs.get(level) or level_programs.get("beginner")

    return {
        "recommended_program": program,
        "days_per_week":       req.days_per_week,
        "equipment":           req.equipment,
        "message": f"This program is tailored for {level} level athletes targeting {goal.replace('_', ' ')}."
    }


@router.get("/challenges")
def get_challenges(goal: Optional[str] = None, difficulty: Optional[str] = None):
    """Get available fitness challenges, optionally filtered."""
    results = CHALLENGES
    if goal:
        results = [c for c in results if c["goal"] == goal]
    if difficulty:
        results = [c for c in results if c["difficulty"] == difficulty]
    return {"total": len(results), "challenges": results}


@router.get("/challenges/{challenge_id}/join")
def join_challenge(challenge_id: str, user_id: str):
    """Join a fitness challenge."""
    challenge = next((c for c in CHALLENGES if c["id"] == challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    return {
        "user_id":       user_id,
        "challenge":     challenge["name"],
        "start_message": f"🎯 You've joined '{challenge['name']}'! Starting today.",
        "daily_target":  challenge["daily_target"],
        "duration":      f"{challenge['duration_days']} days",
        "first_tip":     "Log your progress daily in the Habit Tracker to earn badges!"
    }
