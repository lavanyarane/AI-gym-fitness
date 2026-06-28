import { useState } from "react";
import GymTrainer from "./components/GymTrainer";
import Dietician from "./components/Dietician";
import HabitTracker from "./components/HabitTracker";
import VirtualBuddy from "./components/VirtualBuddy";
import PoseAnalyzer from "./components/PoseAnalyzer";
import GymRecommender from "./components/GymRecommender";
import SmartGym from "./components/SmartGym";
import "./App.css";

const MODULES = [
  { id: "trainer",     label: "🏋️ Gym Trainer",      component: GymTrainer },
  { id: "diet",        label: "🥗 Dietician",         component: Dietician },
  { id: "smartgym",    label: "📡 Smart Gym",         component: SmartGym },
  { id: "habit",       label: "📊 Habit Tracker",     component: HabitTracker },
  { id: "buddy",       label: "🤖 Virtual Buddy",     component: VirtualBuddy },
  { id: "pose",        label: "🎯 Pose Analyzer",     component: PoseAnalyzer },
  { id: "recommender", label: "🗺️ Gym Recommender",  component: GymRecommender },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("trainer");
  const ActiveComponent = MODULES.find(m => m.id === activeTab)?.component;

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <div>
              <h1>AI Gym & Fitness Assistant</h1>
              <p>Your intelligent fitness ecosystem</p>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="tab-nav">
        <div className="tab-scroll">
          {MODULES.map(m => (
            <button
              key={m.id}
              className={`tab-btn ${activeTab === m.id ? "active" : ""}`}
              onClick={() => setActiveTab(m.id)}
            >
              {m.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Active Module */}
      <main className="main-content">
        {ActiveComponent && <ActiveComponent />}
      </main>
    </div>
  );
}
