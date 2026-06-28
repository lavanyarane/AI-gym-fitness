"""
Module 6: Pose-to-Performance Analyzer
Scores workout performance using motion efficiency analysis,
creates a 'Performance Score' with weekly progress reports.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict

router = APIRouter()


class PoseSession(BaseModel):
    user_id: str
    exercise: str
    sets_completed: int
    reps_per_set: List[int]
    form_scores: List[float]        # 0–100 per set
    joint_angles: Optional[List[Dict]] = []
    duration_seconds: int

class WeeklyData(BaseModel):
    user_id: str
    sessions: List[Dict]            # list of {date, exercise, performance_score}


def compute_performance_score(session: PoseSession) -> dict:
    """Compute an overall performance score for a session."""
    avg_form        = sum(session.form_scores) / len(session.form_scores) if session.form_scores else 0
    total_reps      = sum(session.reps_per_set)
    consistency     = (1 - (max(session.reps_per_set) - min(session.reps_per_set)) / max(max(session.reps_per_set), 1)) * 100
    completion_pct  = (session.sets_completed / 3) * 100   # assume 3 target sets

    # Weighted composite score
    performance_score = (
        avg_form    * 0.40 +
        consistency * 0.30 +
        min(completion_pct, 100) * 0.30
    )

    if performance_score >= 85:
        grade, label = "A", "Elite"
    elif performance_score >= 70:
        grade, label = "B", "Strong"
    elif performance_score >= 55:
        grade, label = "C", "Developing"
    else:
        grade, label = "D", "Needs Work"

    improvements = []
    if avg_form < 70:
        improvements.append("Focus on form — quality > quantity")
    if consistency < 60:
        improvements.append("Aim for consistent reps per set — fatigue management needed")
    if completion_pct < 100:
        improvements.append("Try to complete all planned sets next session")

    return {
        "performance_score": round(performance_score, 1),
        "grade":             grade,
        "label":             label,
        "breakdown": {
            "form_score":         round(avg_form, 1),
            "consistency_score":  round(consistency, 1),
            "completion_score":   round(min(completion_pct, 100), 1)
        },
        "total_reps":      total_reps,
        "improvements":    improvements if improvements else ["✅ Excellent session — no major corrections!"]
    }


@router.post("/analyze-session")
def analyze_session(session: PoseSession):
    """Analyze a full workout session and return performance score."""
    if not session.form_scores:
        raise HTTPException(status_code=400, detail="form_scores list cannot be empty")

    result = compute_performance_score(session)

    return {
        "user_id":     session.user_id,
        "exercise":    session.exercise,
        "duration_seconds": session.duration_seconds,
        "analysis":    result,
        "badges":      ["🏋️ Workout Complete"] + (
            ["🎯 Perfect Form"] if result["breakdown"]["form_score"] >= 90 else []
        ) + (
            ["🔥 Consistent Sets"] if result["breakdown"]["consistency_score"] >= 85 else []
        )
    }


@router.post("/weekly-performance")
def weekly_performance_report(data: WeeklyData):
    """Generate a weekly performance trend report."""
    if not data.sessions:
        raise HTTPException(status_code=400, detail="No sessions provided")

    scores = [s.get("performance_score", 0) for s in data.sessions]
    avg    = round(sum(scores) / len(scores), 1)

    # Trend: compare first half vs second half
    mid       = len(scores) // 2
    first_avg = sum(scores[:mid]) / max(mid, 1)
    last_avg  = sum(scores[mid:]) / max(len(scores) - mid, 1)
    trend     = "improving" if last_avg > first_avg else "declining" if last_avg < first_avg else "stable"

    return {
        "user_id":       data.user_id,
        "sessions_count": len(data.sessions),
        "average_score": avg,
        "highest_score": max(scores),
        "lowest_score":  min(scores),
        "trend":         trend,
        "trend_message": (
            "📈 You're improving week by week — keep the momentum!" if trend == "improving" else
            "📉 Slight dip this week — rest, refocus, and bounce back!" if trend == "declining" else
            "➡️ Consistent performance — push harder next week for growth!"
        ),
        "weekly_grade": "A" if avg >= 85 else "B" if avg >= 70 else "C"
    }


@router.get("/efficiency-tips/{exercise}")
def get_efficiency_tips(exercise: str):
    """Get motion efficiency tips for a specific exercise."""
    tips = {
        "squat": {
            "key_joints": ["Knee", "Hip", "Ankle"],
            "optimal_angles": {"knee": "85–95°", "hip": "80–100°"},
            "tips": [
                "Keep knees tracking over toes",
                "Chest upright, not leaning forward",
                "Drive through heels on the way up",
                "Brace core throughout the movement"
            ]
        },
        "pushup": {
            "key_joints": ["Elbow", "Shoulder", "Wrist"],
            "optimal_angles": {"elbow": "90° at bottom", "body": "Straight line"},
            "tips": [
                "Lower until chest nearly touches ground",
                "Keep body rigid — no hip sag",
                "Elbows at 45° — not flared out",
                "Full lockout at the top"
            ]
        },
        "bicep_curl": {
            "key_joints": ["Elbow", "Wrist"],
            "optimal_angles": {"elbow": "Full ROM 10°–145°"},
            "tips": [
                "Elbows stay pinned at your sides",
                "Squeeze at the top for 1 second",
                "Slow eccentric (3 sec down)",
                "Avoid swinging torso"
            ]
        },
        "deadlift": {
            "key_joints": ["Hip", "Knee", "Spine"],
            "optimal_angles": {"hip": "Hinge 90–110°", "spine": "Neutral"},
            "tips": [
                "Keep bar close to body throughout",
                "Hinge at hips, not rounding lower back",
                "Drive hips forward at lockout",
                "Brace core before lifting"
            ]
        }
    }

    ex = exercise.lower()
    if ex not in tips:
        raise HTTPException(status_code=404, detail=f"Exercise '{exercise}' not found. Available: {list(tips.keys())}")

    return {"exercise": exercise, **tips[ex]}
