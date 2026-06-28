"""
Module 4: AI Fitness Habit Tracker (Behavioral AI)
Predicts skip risk, sends motivational nudges, adjusts schedules dynamically.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import random

router = APIRouter()


# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────
class HabitProfile(BaseModel):
    user_id: str
    name: str
    workout_days: List[str]         # ["Monday", "Wednesday", "Friday"]
    preferred_time: str             # "morning" / "evening" / "night"
    streak_days: int = 0
    total_workouts: int = 0
    missed_last_week: int = 0
    stress_level: int = 5           # 1–10
    sleep_hours: float = 7.0
    motivation_style: str = "data"  # "data" / "inspirational" / "competitive"

class WorkoutLog(BaseModel):
    user_id: str
    date: str
    completed: bool
    duration_minutes: Optional[int] = 0
    notes: Optional[str] = ""

class ProgressData(BaseModel):
    user_id: str
    weekly_logs: List[Dict]         # list of {date, completed, duration}


# ──────────────────────────────────────────────
# Motivational messages
# ──────────────────────────────────────────────
MOTIVATIONAL_MESSAGES = {
    "data": [
        "📊 Your consistency rate dropped to {rate}% — just 1 workout closes the gap!",
        "📈 You're 3 sessions away from your personal best streak!",
        "🔥 Data shows your performance peaks on {day} — don't miss it!",
    ],
    "inspirational": [
        "💪 Every rep you do today is an investment in the person you're becoming.",
        "🌟 The only bad workout is the one that didn't happen. Show up today!",
        "🏆 Champions are made in the moments they want to quit most. Keep going!",
    ],
    "competitive": [
        "⚡ 3 users on the leaderboard worked out today — don't fall behind!",
        "🥇 Your streak is at risk — top performers don't miss consecutive days!",
        "📉 Your rank dropped 2 positions this week — one workout can change that!",
    ]
}

SKIP_RISK_FACTORS = {
    "missed_last_week": 0.3,
    "high_stress":      0.25,
    "low_sleep":        0.2,
    "monday_skip":      0.15,
    "evening_only":     0.1,
}


# ──────────────────────────────────────────────
# Core ML-like prediction
# ──────────────────────────────────────────────
def predict_skip_risk(profile: HabitProfile) -> dict:
    """Rule-based behavioral model to predict workout skip probability."""
    risk_score = 0.0
    risk_factors = []

    if profile.missed_last_week >= 2:
        risk_score += 0.30
        risk_factors.append(f"Missed {profile.missed_last_week} workouts last week")
    if profile.stress_level >= 7:
        risk_score += 0.25
        risk_factors.append(f"High stress level ({profile.stress_level}/10)")
    if profile.sleep_hours < 6:
        risk_score += 0.20
        risk_factors.append(f"Low sleep ({profile.sleep_hours}h — under 6h)")
    if profile.streak_days == 0:
        risk_score += 0.15
        risk_factors.append("No active streak — hard to restart")
    if profile.preferred_time == "night":
        risk_score += 0.10
        risk_factors.append("Night workouts have 20% higher skip rate")

    risk_score = min(risk_score, 1.0)

    if risk_score >= 0.7:
        level = "HIGH"
    elif risk_score >= 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "skip_probability": round(risk_score * 100, 1),
        "risk_level":       level,
        "risk_factors":     risk_factors
    }


def generate_nudge(profile: HabitProfile, risk_level: str) -> str:
    """Generate a personalized motivational nudge."""
    messages = MOTIVATIONAL_MESSAGES.get(profile.motivation_style, MOTIVATIONAL_MESSAGES["inspirational"])
    msg = random.choice(messages)

    # Fill in dynamic placeholders
    today = datetime.now().strftime("%A")
    consistency = max(0, 100 - (profile.missed_last_week * 15))
    msg = msg.replace("{rate}", str(consistency))
    msg = msg.replace("{day}", today)

    return msg


def adjust_schedule(profile: HabitProfile) -> list:
    """Dynamically adjust workout schedule based on behavior."""
    adjusted = []
    day_map   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    for day in profile.workout_days:
        entry = {"day": day, "status": "scheduled", "adjustment": None}

        # If high skip risk on that day, suggest a swap
        if profile.stress_level >= 8 and day in ["Monday", "Friday"]:
            entry["adjustment"] = "Consider shifting to Wednesday — lower skip rate midweek"
        elif profile.sleep_hours < 6 and profile.preferred_time == "morning":
            entry["adjustment"] = "Poor sleep detected — shift to evening session today"

        adjusted.append(entry)

    return adjusted


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@router.post("/predict-skip")
def predict_skip(profile: HabitProfile):
    """Predict likelihood of skipping next workout."""
    prediction = predict_skip_risk(profile)
    nudge      = generate_nudge(profile, prediction["risk_level"])
    schedule   = adjust_schedule(profile)

    return {
        "user":         profile.name,
        "prediction":   prediction,
        "nudge":        nudge,
        "adjusted_schedule": schedule,
        "streak_status": {
            "current_streak": profile.streak_days,
            "message": f"🔥 {profile.streak_days} day streak!" if profile.streak_days > 0 else "Start a new streak today!",
            "next_milestone": 7 if profile.streak_days < 7 else 30
        }
    }


@router.post("/log-workout")
def log_workout(log: WorkoutLog):
    """Log a completed or missed workout and update streak."""
    if log.completed:
        message = f"✅ Workout logged for {log.date}! Great job!"
        points  = 10 + (log.duration_minutes // 10)
        badge   = "🏋️ Workout Done" if log.duration_minutes >= 30 else "⚡ Quick Session"
    else:
        message = f"📝 Rest day logged for {log.date}. Recovery is part of training!"
        points  = 2
        badge   = "😴 Rest Day"

    return {
        "user_id":     log.user_id,
        "date":        log.date,
        "completed":   log.completed,
        "duration":    log.duration_minutes,
        "points_earned": points,
        "badge":        badge,
        "message":      message,
        "notes":        log.notes
    }


@router.post("/weekly-report")
def generate_weekly_report(data: ProgressData):
    """Generate a weekly progress report."""
    completed = [d for d in data.weekly_logs if d.get("completed")]
    missed    = [d for d in data.weekly_logs if not d.get("completed")]
    total_min = sum(d.get("duration", 0) for d in completed)
    consistency = round((len(completed) / len(data.weekly_logs)) * 100, 1) if data.weekly_logs else 0

    return {
        "user_id":             data.user_id,
        "week_summary": {
            "workouts_completed": len(completed),
            "workouts_missed":    len(missed),
            "total_minutes":      total_min,
            "consistency_rate":   f"{consistency}%",
            "grade": "A" if consistency >= 80 else "B" if consistency >= 60 else "C"
        },
        "trend": "improving" if consistency >= 70 else "needs_attention",
        "next_week_goal": f"Complete {min(len(completed) + 1, 7)} workouts next week",
        "insight": (
            "🌟 Amazing consistency! You're in the top 10% of users!"
            if consistency >= 80 else
            "💡 Tip: Schedule workouts like meetings — block time in your calendar!"
        )
    }


@router.get("/leaderboard/{timeframe}")
def get_leaderboard(timeframe: str = "weekly"):
    """Get fitness leaderboard to motivate competitive users."""
    mock_board = [
        {"rank": 1, "name": "Rahul M.",    "workouts": 7, "streak": 21, "points": 420},
        {"rank": 2, "name": "Sneha P.",    "workouts": 6, "streak": 14, "points": 380},
        {"rank": 3, "name": "Arjun K.",    "workouts": 6, "streak": 10, "points": 355},
        {"rank": 4, "name": "Priya S.",    "workouts": 5, "streak": 8,  "points": 310},
        {"rank": 5, "name": "You",         "workouts": 4, "streak": 5,  "points": 265},
    ]
    return {
        "timeframe":   timeframe,
        "leaderboard": mock_board,
        "your_rank":   5,
        "to_next_rank": "1 more workout to beat Priya!"
    }
