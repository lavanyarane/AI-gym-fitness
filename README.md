# ⚡ AI Gym & Fitness Assistant
### Unlox Academy — Major Project | Lavanya Rane | B.Tech AI & ML, MIT-ADT University

---

## 📌 Project Overview
A unified AI-powered fitness ecosystem with 7 intelligent modules:

| # | Module | Technology |
|---|--------|-----------|
| 1 | 🏋️ AI Gym Trainer | MediaPipe, OpenCV, Pose Detection |
| 2 | 🥗 AI Dietician & Calorie Coach | NLP, BMI Calculation, Meal Planning |
| 3 | 📡 Smart Gym Assistant | IoT Simulation, HR Zone Analysis |
| 4 | 📊 AI Fitness Habit Tracker | Behavioral AI, Skip Prediction |
| 5 | 🤖 Virtual Gym Buddy | Sentiment Analysis, Conversational AI |
| 6 | 🎯 Pose-to-Performance Analyzer | Motion Efficiency, Performance Scoring |
| 7 | 🗺️ Gym Recommender & Planner | Recommendation Engine, Challenge System |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js + Vite |
| Backend | Python FastAPI |
| AI/ML | MediaPipe, OpenCV, scikit-learn |
| Conversational AI | Sentiment Analysis + Rule-based NLP |
| Analytics | Custom scoring algorithms |

---

## 🚀 Setup Instructions

### Step 1: Backend Setup

```bash
# Navigate to backend folder
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

Backend runs at: **http://localhost:8000**
API Docs at: **http://localhost:8000/docs**

---

### Step 2: Frontend Setup

```bash
# Navigate to frontend folder
cd frontend

# Install Node dependencies
npm install

# Start the React app
npm run dev
```

Frontend runs at: **http://localhost:3000**

---

## 📁 Project Structure

```
ai-gym-fitness/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── requirements.txt           # Python dependencies
│   └── routers/
│       ├── gym_trainer.py         # Module 1: Pose Detection
│       ├── dietician.py           # Module 2: Diet Planning
│       ├── smart_gym.py           # Module 3: IoT Monitoring
│       ├── habit_tracker.py       # Module 4: Behavioral AI
│       ├── virtual_buddy.py       # Module 5: Chat Companion
│       ├── pose_analyzer.py       # Module 6: Performance Scoring
│       └── gym_recommender.py     # Module 7: Recommendations
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx                # Main app with tab navigation
        ├── App.css                # Dark fitness theme
        └── components/
            ├── GymTrainer.jsx
            ├── Dietician.jsx
            ├── SmartGym.jsx
            ├── HabitTracker.jsx
            ├── VirtualBuddy.jsx
            ├── PoseAnalyzer.jsx
            └── GymRecommender.jsx
```

---

## 🔗 API Endpoints Summary

### Module 1 — AI Gym Trainer
- `POST /api/gym-trainer/analyze-frame` — Analyze pose from image
- `POST /api/gym-trainer/generate-plan` — Generate workout plan
- `GET  /api/gym-trainer/exercises` — List supported exercises

### Module 2 — AI Dietician
- `POST /api/dietician/diet-plan` — Get personalized diet plan
- `POST /api/dietician/grocery-list` — Get weekly grocery list
- `POST /api/dietician/track-meal` — Log and analyze a meal

### Module 3 — Smart Gym
- `POST /api/smart-gym/monitor` — Monitor IoT sensor data
- `POST /api/smart-gym/adjust-resistance` — Auto-adjust resistance
- `GET  /api/smart-gym/equipment-status` — Check equipment availability

### Module 4 — Habit Tracker
- `POST /api/habit-tracker/predict-skip` — Predict skip risk
- `POST /api/habit-tracker/log-workout` — Log workout
- `GET  /api/habit-tracker/leaderboard/weekly` — Get leaderboard

### Module 5 — Virtual Buddy
- `POST /api/virtual-buddy/chat` — Chat with AI buddy
- `POST /api/virtual-buddy/analyze-emotion` — Emotion detection
- `GET  /api/virtual-buddy/daily-quote` — Daily motivation quote

### Module 6 — Pose Analyzer
- `POST /api/pose-analyzer/analyze-session` — Score a session
- `POST /api/pose-analyzer/weekly-performance` — Weekly report
- `GET  /api/pose-analyzer/efficiency-tips/{exercise}` — Form tips

### Module 7 — Gym Recommender
- `POST /api/gym-recommender/recommend-gyms` — Find nearby gyms
- `POST /api/gym-recommender/recommend-program` — Get a program
- `GET  /api/gym-recommender/challenges` — Browse challenges

---

## 📊 Deliverables Completed

- [x] Module 1: AI Gym Trainer with MediaPipe pose detection
- [x] Module 2: AI Dietician with BMI, TDEE, and meal planning
- [x] Module 3: Smart Gym IoT integration and HR zone monitoring
- [x] Module 4: Behavioral AI for habit tracking and skip prediction
- [x] Module 5: Virtual Gym Buddy with sentiment analysis
- [x] Module 6: Pose-to-Performance Analyzer with grading system
- [x] Module 7: Gym Recommender with programs and challenges
- [x] React Frontend Dashboard with all 7 modules
- [x] FastAPI Backend with full REST API

---

*Submitted by: Lavanya Rane | Unlox Academy AI/ML Internship | MIT-ADT University, Pune*
