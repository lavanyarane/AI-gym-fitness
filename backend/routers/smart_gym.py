"""
Module 3: Smart Gym Assistant (AI + IoT Integration)
Monitors equipment performance, adjusts resistance, and recommends rest/intensity.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import random, math

router = APIRouter()


class IoTSensorData(BaseModel):
    equipment_id: str
    equipment_type: str        # "treadmill" / "bike" / "resistance_machine"
    current_resistance: float  # 0–100
    current_speed: float       # km/h (for cardio)
    heart_rate: int            # bpm
    calories_burned: float
    session_minutes: float
    user_fitness_level: str    # "beginner" / "intermediate" / "advanced"

class EquipmentStatus(BaseModel):
    equipment_id: str
    status: str                # "available" / "in_use" / "maintenance"
    equipment_type: str
    current_user: Optional[str] = None


# ──────────────────────────────────────────────
# Heart Rate Zones
# ──────────────────────────────────────────────
def get_hr_zone(hr: int, age: int = 25) -> dict:
    max_hr = 220 - age
    pct    = (hr / max_hr) * 100
    if pct < 50:
        zone, name = 1, "Rest"
    elif pct < 60:
        zone, name = 2, "Fat Burn"
    elif pct < 70:
        zone, name = 3, "Cardio"
    elif pct < 85:
        zone, name = 4, "Anaerobic"
    else:
        zone, name = 5, "Max Effort"
    return {"zone": zone, "name": name, "percent_max": round(pct, 1)}


@router.post("/monitor")
def monitor_performance(data: IoTSensorData):
    """Real-time performance monitoring from IoT sensors."""
    hr_zone     = get_hr_zone(data.heart_rate)
    suggestions = []
    adjustments = {}

    # Intensity recommendations based on HR zone and fitness level
    if data.heart_rate > 180:
        suggestions.append("🛑 Heart rate very high — reduce intensity immediately")
        adjustments["resistance"] = max(data.current_resistance - 20, 0)
        adjustments["speed"]      = max(data.current_speed - 2, 0)
    elif data.heart_rate < 100 and data.user_fitness_level != "beginner":
        suggestions.append("📈 Heart rate low — increase intensity for better results")
        adjustments["resistance"] = min(data.current_resistance + 10, 100)
    else:
        suggestions.append("✅ Current intensity is in optimal range")
        adjustments["resistance"] = data.current_resistance
        adjustments["speed"]      = data.current_speed

    # Rest recommendation
    rest_needed = False
    if data.session_minutes > 45:
        rest_needed = True
        suggestions.append("⏸️ You've been exercising 45+ min — take a 2-minute rest")
    if data.heart_rate > 170:
        rest_needed = True
        suggestions.append("⏸️ High HR — rest for 90 seconds before continuing")

    # Calorie pace
    cal_per_min = data.calories_burned / max(data.session_minutes, 1)

    return {
        "equipment":        data.equipment_id,
        "session_minutes":  data.session_minutes,
        "heart_rate_zone":  hr_zone,
        "calories_burned":  round(data.calories_burned, 1),
        "cal_per_minute":   round(cal_per_min, 1),
        "rest_recommended": rest_needed,
        "suggested_adjustments": adjustments,
        "recommendations":  suggestions,
        "performance_rating": "Excellent" if hr_zone["zone"] in [3, 4] else "Good"
    }


@router.post("/adjust-resistance")
def auto_adjust_resistance(data: IoTSensorData):
    """Auto-adjust resistance based on heart rate target zone."""
    target_zones = {
        "beginner":     {"min": 50, "max": 65},
        "intermediate": {"min": 65, "max": 75},
        "advanced":     {"min": 75, "max": 88},
    }
    zone = target_zones.get(data.user_fitness_level, target_zones["intermediate"])
    max_hr   = 195
    current_pct = (data.heart_rate / max_hr) * 100

    if current_pct < zone["min"]:
        new_resistance = min(data.current_resistance + 5, 100)
        action = "increased"
    elif current_pct > zone["max"]:
        new_resistance = max(data.current_resistance - 5, 0)
        action = "decreased"
    else:
        new_resistance = data.current_resistance
        action = "maintained"

    return {
        "equipment_id":       data.equipment_id,
        "previous_resistance": data.current_resistance,
        "new_resistance":      new_resistance,
        "action":              action,
        "reason": f"HR {data.heart_rate} bpm — target zone {zone['min']}–{zone['max']}% max HR",
        "target_hr_range": {
            "min": int(max_hr * zone["min"] / 100),
            "max": int(max_hr * zone["max"] / 100)
        }
    }


@router.get("/equipment-status")
def get_equipment_status():
    """Get real-time status of all gym equipment (simulated IoT feed)."""
    equipment_list = [
        {"id": "TM-01", "type": "Treadmill",          "status": "available"},
        {"id": "TM-02", "type": "Treadmill",          "status": "in_use",  "user": "User A"},
        {"id": "BC-01", "type": "Stationary Bike",    "status": "available"},
        {"id": "BC-02", "type": "Stationary Bike",    "status": "in_use",  "user": "User B"},
        {"id": "RM-01", "type": "Resistance Machine", "status": "available"},
        {"id": "RM-02", "type": "Resistance Machine", "status": "maintenance"},
        {"id": "EL-01", "type": "Elliptical",         "status": "available"},
        {"id": "RW-01", "type": "Rowing Machine",     "status": "available"},
    ]
    available_count = sum(1 for e in equipment_list if e["status"] == "available")
    return {
        "total_equipment": len(equipment_list),
        "available":        available_count,
        "in_use":           sum(1 for e in equipment_list if e["status"] == "in_use"),
        "maintenance":      sum(1 for e in equipment_list if e["status"] == "maintenance"),
        "equipment":        equipment_list
    }


@router.get("/rest-timer/{intensity_level}")
def get_rest_recommendation(intensity_level: str):
    """Get recommended rest time based on workout intensity."""
    rest_times = {
        "low":    {"seconds": 30,  "tip": "Light activity during rest — walk around"},
        "medium": {"seconds": 60,  "tip": "Controlled breathing, stay loose"},
        "high":   {"seconds": 90,  "tip": "Sit down, hydrate, deep breaths"},
        "max":    {"seconds": 180, "tip": "Full rest — lie down if needed, sip water"},
    }
    rest = rest_times.get(intensity_level, rest_times["medium"])
    return {
        "intensity_level":   intensity_level,
        "rest_seconds":      rest["seconds"],
        "rest_tip":          rest["tip"],
        "next_set_cue":      "Begin next set when HR drops below 120 bpm"
    }
