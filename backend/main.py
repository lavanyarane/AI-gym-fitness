"""
AI Gym & Fitness Assistant — Main FastAPI Backend
Modules: Gym Trainer, Dietician, Smart Gym, Habit Tracker,
         Virtual Buddy, Pose Analyzer, Gym Recommender
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# ── Module routers ──
from routers import gym_trainer, dietician, habit_tracker, virtual_buddy, pose_analyzer, gym_recommender, smart_gym

app = FastAPI(
    title="AI Gym & Fitness Assistant",
    description="Unified AI-powered fitness ecosystem",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register all module routers ──
app.include_router(gym_trainer.router,     prefix="/api/gym-trainer",    tags=["AI Gym Trainer"])
app.include_router(dietician.router,       prefix="/api/dietician",       tags=["AI Dietician"])
app.include_router(smart_gym.router,       prefix="/api/smart-gym",       tags=["Smart Gym"])
app.include_router(habit_tracker.router,   prefix="/api/habit-tracker",   tags=["Habit Tracker"])
app.include_router(virtual_buddy.router,   prefix="/api/virtual-buddy",   tags=["Virtual Buddy"])
app.include_router(pose_analyzer.router,   prefix="/api/pose-analyzer",   tags=["Pose Analyzer"])
app.include_router(gym_recommender.router, prefix="/api/gym-recommender", tags=["Gym Recommender"])

@app.get("/")
def root():
    return {"message": "AI Gym & Fitness Assistant API is running ✅"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
