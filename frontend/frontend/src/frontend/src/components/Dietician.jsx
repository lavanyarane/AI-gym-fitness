import { useState } from "react";
const API = "http://localhost:8000/api";

export default function Dietician() {
  const [form, setForm] = useState({ name: "Lavanya", age: 20, gender: "female", height_cm: 162, weight_kg: 55, goal: "maintain", activity_level: "moderate", dietary_preference: "vegetarian", allergies: [] });
  const [plan, setPlan] = useState(null);
  const [grocery, setGrocery] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mealLog, setMealLog] = useState({ meal_name: "", calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 });
  const [mealResult, setMealResult] = useState(null);

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const getDietPlan = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/dietician/diet-plan`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, age: +form.age, height_cm: +form.height_cm, weight_kg: +form.weight_kg }) });
      setPlan(await res.json());
    } catch { alert("Backend not running!"); }
    setLoading(false);
  };

  const getGrocery = async () => {
    try {
      const res = await fetch(`${API}/dietician/grocery-list`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, age: +form.age, height_cm: +form.height_cm, weight_kg: +form.weight_kg }) });
      setGrocery(await res.json());
    } catch {}
  };

  const trackMeal = async () => {
    try {
      const res = await fetch(`${API}/dietician/track-meal`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...mealLog, calories: +mealLog.calories, protein_g: +mealLog.protein_g, carbs_g: +mealLog.carbs_g, fat_g: +mealLog.fat_g }) });
      setMealResult(await res.json());
    } catch {}
  };

  return (
    <div>
      <div className="module-header"><h2>🥗 AI Dietician & Calorie Coach</h2><p>Personalized diet plans, grocery lists, and meal tracking powered by AI</p></div>
      <div className="grid-2">
        {/* Profile Form */}
        <div className="card">
          <div className="card-title">👤 Your Profile</div>
          <div className="grid-2">
            {[["Name","name","text"],["Age","age","number"],["Height (cm)","height_cm","number"],["Weight (kg)","weight_kg","number"]].map(([label,key,type]) => (
              <div className="form-group" key={key}>
                <label>{label}</label>
                <input type={type} value={form[key]} onChange={e => update(key, e.target.value)} />
              </div>
            ))}
          </div>
          <div className="grid-2">
            <div className="form-group"><label>Gender</label>
              <select value={form.gender} onChange={e => update("gender", e.target.value)}>
                <option value="female">Female</option><option value="male">Male</option>
              </select>
            </div>
            <div className="form-group"><label>Goal</label>
              <select value={form.goal} onChange={e => update("goal", e.target.value)}>
                <option value="lose_weight">Lose Weight</option><option value="gain_muscle">Gain Muscle</option><option value="maintain">Maintain</option>
              </select>
            </div>
            <div className="form-group"><label>Activity Level</label>
              <select value={form.activity_level} onChange={e => update("activity_level", e.target.value)}>
                <option value="sedentary">Sedentary</option><option value="light">Light</option><option value="moderate">Moderate</option><option value="active">Active</option><option value="very_active">Very Active</option>
              </select>
            </div>
            <div className="form-group"><label>Diet Preference</label>
              <select value={form.dietary_preference} onChange={e => update("dietary_preference", e.target.value)}>
                <option value="vegetarian">Vegetarian</option><option value="vegan">Vegan</option><option value="non-vegetarian">Non-Vegetarian</option><option value="keto">Keto</option>
              </select>
            </div>
          </div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <button className="btn btn-primary" onClick={getDietPlan} disabled={loading}>
              {loading ? "Generating..." : "🥗 Get Diet Plan"}
            </button>
            <button className="btn btn-secondary" onClick={getGrocery}>🛒 Grocery List</button>
          </div>
        </div>

        {/* Diet Plan Result */}
        <div className="card">
          <div className="card-title">📋 Your Personalized Diet Plan</div>
          {plan ? (
            <div>
              <div className="grid-3" style={{ marginBottom: "1rem" }}>
                <div className="result-box" style={{ textAlign: "center" }}>
                  <div className="score-number" style={{ fontSize: "1.8rem" }}>{plan.daily_calorie_target}</div>
                  <div className="score-label">Daily kcal Target</div>
                </div>
                <div className="result-box" style={{ textAlign: "center" }}>
                  <div className="score-number" style={{ fontSize: "1.8rem" }}>{plan.bmi?.bmi}</div>
                  <div className="score-label">BMI ({plan.bmi?.category})</div>
                </div>
                <div className="result-box" style={{ textAlign: "center" }}>
                  <div className="score-number" style={{ fontSize: "1.8rem" }}>{plan.hydration_goal_liters}L</div>
                  <div className="score-label">Daily Water</div>
                </div>
              </div>
              {plan.meal_plan && Object.entries(plan.meal_plan).map(([meal, data]) => (
                <div key={meal} className="stat-row">
                  <span className="stat-label" style={{ textTransform: "capitalize" }}>{meal.replace(/_/g, " ")}</span>
                  <span className="stat-value">{data.name} — {data.cal} kcal</span>
                </div>
              ))}
              <div style={{ marginTop: "0.75rem" }}>
                {plan.notes?.map((n, i) => <div key={i} style={{ fontSize: "0.8rem", color: "var(--text2)", marginBottom: "0.25rem" }}>{n}</div>)}
              </div>
            </div>
          ) : (
            <div style={{ color: "var(--text2)", fontSize: "0.875rem" }}>Fill in your profile and click "Get Diet Plan" 👆</div>
          )}
        </div>

        {/* Grocery List */}
        {grocery && (
          <div className="card">
            <div className="card-title">🛒 Weekly Grocery List</div>
            {Object.entries(grocery.weekly_grocery_list).map(([cat, items]) => (
              <div key={cat} style={{ marginBottom: "0.75rem" }}>
                <div style={{ fontSize: "0.75rem", color: "var(--accent)", textTransform: "uppercase", fontWeight: 700, marginBottom: "0.35rem" }}>{cat}</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                  {items.map(item => <span key={item} className="badge badge-blue">{item}</span>)}
                </div>
              </div>
            ))}
            <p style={{ marginTop: "0.75rem", fontSize: "0.8rem", color: "var(--text2)" }}>💡 {grocery.tip}</p>
          </div>
        )}

        {/* Meal Tracker */}
        <div className="card">
          <div className="card-title">📝 Track a Meal</div>
          <div className="form-group"><label>Meal Name</label>
            <input value={mealLog.meal_name} onChange={e => setMealLog(m => ({ ...m, meal_name: e.target.value }))} placeholder="e.g. Dal Rice" />
          </div>
          <div className="grid-2">
            {[["Calories","calories"],["Protein (g)","protein_g"],["Carbs (g)","carbs_g"],["Fat (g)","fat_g"]].map(([label,key]) => (
              <div className="form-group" key={key}><label>{label}</label>
                <input type="number" value={mealLog[key]} onChange={e => setMealLog(m => ({ ...m, [key]: e.target.value }))} />
              </div>
            ))}
          </div>
          <button className="btn btn-primary" onClick={trackMeal}>Log Meal</button>
          {mealResult && (
            <div className="result-box" style={{ marginTop: "1rem" }}>
              {mealResult.feedback?.map((f, i) => <div key={i} style={{ fontSize: "0.875rem", marginBottom: "0.25rem" }}>{f}</div>)}
              <div style={{ marginTop: "0.5rem", fontSize: "0.8rem", color: "var(--text2)" }}>
                Protein: {mealResult.macro_split_percent?.protein}% | Carbs: {mealResult.macro_split_percent?.carbs}% | Fat: {mealResult.macro_split_percent?.fat}%
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
