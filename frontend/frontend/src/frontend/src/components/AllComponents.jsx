// GymTrainer.jsx
import { useState } from "react";
const API = "http://localhost:8000/api";

export function GymTrainer() {
  const [exercise, setExercise] = useState("squat");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeFrame = async () => {
    if (!file) return alert("Please select an image first");
    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res = await fetch(`${API}/gym-trainer/analyze-frame?exercise=${exercise}`, { method: "POST", body: fd });
      setResult(await res.json());
    } catch { alert("Backend not running! Start with: uvicorn main:app --reload"); }
    setLoading(false);
  };

  const getPlan = async () => {
    try {
      const res = await fetch(`${API}/gym-trainer/generate-plan`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ exercise, target_reps: 10, target_sets: 3 }) });
      setPlan(await res.json());
    } catch {}
  };

  return (
    <div>
      <div className="module-header"><h2>🏋️ AI Gym Trainer</h2><p>Real-time pose detection, form analysis, and rep counting using MediaPipe</p></div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">📸 Analyze Your Form</div>
          <div className="form-group"><label>Exercise</label>
            <select value={exercise} onChange={e => setExercise(e.target.value)}>
              <option value="squat">Squat</option>
              <option value="pushup">Push-Up</option>
              <option value="bicep_curl">Bicep Curl</option>
            </select>
          </div>
          <div className="form-group"><label>Upload Frame / Photo</label>
            <input type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} style={{ padding: "0.5rem" }} />
          </div>
          {file && <img src={URL.createObjectURL(file)} alt="preview" style={{ width: "100%", borderRadius: 8, marginBottom: "1rem", maxHeight: 200, objectFit: "cover" }} />}
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button className="btn btn-primary" onClick={analyzeFrame} disabled={loading}>{loading ? "Analyzing..." : "🔍 Analyze Form"}</button>
            <button className="btn btn-secondary" onClick={getPlan}>📋 Get Workout Plan</button>
          </div>
        </div>

        <div className="card">
          <div className="card-title">📊 Analysis Result</div>
          {result ? (
            <>
              <div className="score-display">
                <div className="score-number">{result.form_score}</div>
                <div className="score-label">Form Score / 100</div>
              </div>
              <ul className="feedback-list">
                {result.feedback?.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
              {result.joint_angles && Object.entries(result.joint_angles).length > 0 && (
                <div style={{ marginTop: "1rem" }}>
                  <div className="result-title">Joint Angles</div>
                  {Object.entries(result.joint_angles).map(([k, v]) => (
                    <div className="stat-row" key={k}>
                      <span className="stat-label">{k.replace("_", " ")}</span>
                      <span className="stat-value">{v}°</span>
                    </div>
                  ))}
                </div>
              )}
              {result.annotated_image_b64 && (
                <img src={`data:image/jpeg;base64,${result.annotated_image_b64}`} alt="annotated" style={{ width: "100%", borderRadius: 8, marginTop: "1rem" }} />
              )}
            </>
          ) : (
            <div style={{ color: "var(--text2)", fontSize: "0.875rem" }}>Upload an image and click Analyze Form 👆</div>
          )}
        </div>

        {plan && (
          <div className="card" style={{ gridColumn: "1 / -1" }}>
            <div className="card-title">📋 Workout Plan — {plan.exercise}</div>
            <div className="grid-3" style={{ marginBottom: "1rem" }}>
              <div className="result-box" style={{ textAlign: "center" }}><div className="score-number" style={{ fontSize: "1.8rem" }}>{plan.total_sets}</div><div className="score-label">Sets</div></div>
              <div className="result-box" style={{ textAlign: "center" }}><div className="score-number" style={{ fontSize: "1.8rem" }}>{plan.total_reps}</div><div className="score-label">Total Reps</div></div>
              <div className="result-box" style={{ textAlign: "center" }}><div className="score-number" style={{ fontSize: "1.8rem" }}>{plan.estimated_time_minutes}</div><div className="score-label">Est. Minutes</div></div>
            </div>
            {plan.plan?.map((s, i) => (
              <div className="stat-row" key={i}>
                <span className="stat-label">Set {s.set}</span>
                <span className="stat-value">{s.reps} reps · {s.rest_seconds}s rest</span>
                <span style={{ fontSize: "0.75rem", color: "var(--accent)", maxWidth: 300, textAlign: "right" }}>{s.cue}</span>
              </div>
            ))}
            <div style={{ marginTop: "1rem" }}>
              <span className="badge badge-green">Warm-up: {plan.warm_up?.join(" → ")}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function HabitTracker() {
  const [form, setForm] = useState({ user_id: "user1", name: "Lavanya", workout_days: ["Monday","Wednesday","Friday"], preferred_time: "morning", streak_days: 5, total_workouts: 22, missed_last_week: 1, stress_level: 4, sleep_hours: 7, motivation_style: "data" });
  const [result, setResult] = useState(null);
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(false);

  const predict = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/habit-tracker/predict-skip`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      setResult(await res.json());
    } catch { alert("Backend not running!"); }
    setLoading(false);
  };

  const getLeaderboard = async () => {
    try {
      const res = await fetch(`${API}/habit-tracker/leaderboard/weekly`);
      setLeaderboard(await res.json());
    } catch {}
  };

  const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
  const toggleDay = d => {
    const days = form.workout_days.includes(d) ? form.workout_days.filter(x => x !== d) : [...form.workout_days, d];
    setForm(f => ({ ...f, workout_days: days }));
  };

  return (
    <div>
      <div className="module-header"><h2>📊 AI Fitness Habit Tracker</h2><p>Behavioral AI to predict skip risk, send nudges, and keep you on track</p></div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">⚙️ Your Habit Profile</div>
          <div className="form-group"><label>Name</label><input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} /></div>
          <div className="form-group">
            <label>Workout Days</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.25rem" }}>
              {DAYS.map(d => (
                <button key={d} className={`btn ${form.workout_days.includes(d) ? "btn-primary" : "btn-secondary"}`} style={{ padding: "0.35rem 0.7rem", fontSize: "0.75rem" }} onClick={() => toggleDay(d)}>{d.slice(0,3)}</button>
              ))}
            </div>
          </div>
          <div className="grid-2">
            <div className="form-group"><label>Streak Days</label><input type="number" value={form.streak_days} onChange={e => setForm(f => ({ ...f, streak_days: +e.target.value }))} /></div>
            <div className="form-group"><label>Missed Last Week</label><input type="number" value={form.missed_last_week} onChange={e => setForm(f => ({ ...f, missed_last_week: +e.target.value }))} /></div>
            <div className="form-group"><label>Stress Level (1-10)</label><input type="number" min="1" max="10" value={form.stress_level} onChange={e => setForm(f => ({ ...f, stress_level: +e.target.value }))} /></div>
            <div className="form-group"><label>Sleep Hours</label><input type="number" step="0.5" value={form.sleep_hours} onChange={e => setForm(f => ({ ...f, sleep_hours: +e.target.value }))} /></div>
          </div>
          <div className="form-group"><label>Motivation Style</label>
            <select value={form.motivation_style} onChange={e => setForm(f => ({ ...f, motivation_style: e.target.value }))}>
              <option value="data">Data-Driven</option><option value="inspirational">Inspirational</option><option value="competitive">Competitive</option>
            </select>
          </div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button className="btn btn-primary" onClick={predict} disabled={loading}>{loading ? "Analyzing..." : "🔮 Predict Skip Risk"}</button>
            <button className="btn btn-secondary" onClick={getLeaderboard}>🏆 Leaderboard</button>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {result && (
            <div className="card">
              <div className="card-title">🔮 Skip Risk Prediction</div>
              <div className="result-box" style={{ textAlign: "center", marginBottom: "1rem" }}>
                <div className="score-number">{result.prediction?.skip_probability}%</div>
                <div className="score-label">Skip Probability</div>
                <span className={`badge ${result.prediction?.risk_level === "HIGH" ? "badge-red" : result.prediction?.risk_level === "MEDIUM" ? "badge-yellow" : "badge-green"}`} style={{ marginTop: "0.5rem" }}>
                  {result.prediction?.risk_level} RISK
                </span>
              </div>
              <div className="result-box" style={{ background: "rgba(0,229,255,0.05)", borderColor: "rgba(0,229,255,0.2)", marginBottom: "1rem" }}>
                <div style={{ fontSize: "0.9rem" }}>💬 {result.nudge}</div>
              </div>
              <div className="stat-row"><span className="stat-label">🔥 Streak</span><span className="stat-value">{result.streak_status?.message}</span></div>
              {result.prediction?.risk_factors?.map((f, i) => (
                <div key={i} style={{ fontSize: "0.8rem", color: "var(--red)", marginTop: "0.35rem" }}>⚠️ {f}</div>
              ))}
            </div>
          )}

          {leaderboard && (
            <div className="card">
              <div className="card-title">🏆 Weekly Leaderboard</div>
              {leaderboard.leaderboard?.map((u, i) => (
                <div className="stat-row" key={i} style={{ background: u.name === "You" ? "rgba(0,229,255,0.05)" : "transparent", borderRadius: 6, padding: "0.5rem" }}>
                  <span style={{ fontWeight: 700, color: i === 0 ? "#f59e0b" : "var(--text2)" }}>#{u.rank}</span>
                  <span className="stat-value">{u.name}</span>
                  <span style={{ fontSize: "0.8rem", color: "var(--text2)" }}>{u.workouts} workouts · 🔥{u.streak}d</span>
                  <span className="badge badge-blue">{u.points} pts</span>
                </div>
              ))}
              <p style={{ marginTop: "0.75rem", fontSize: "0.8rem", color: "var(--accent)" }}>📣 {leaderboard.to_next_rank}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function PoseAnalyzer() {
  const [form, setForm] = useState({ user_id: "user1", exercise: "squat", sets_completed: 3, reps_per_set: [10,9,10], form_scores: [82,78,85], duration_seconds: 420 });
  const [result, setResult] = useState(null);
  const [tips, setTips] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/pose-analyzer/analyze-session`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      setResult(await res.json());
    } catch { alert("Backend not running!"); }
    setLoading(false);
  };

  const getTips = async () => {
    try {
      const res = await fetch(`${API}/pose-analyzer/efficiency-tips/${form.exercise}`);
      setTips(await res.json());
    } catch {}
  };

  return (
    <div>
      <div className="module-header"><h2>🎯 Pose-to-Performance Analyzer</h2><p>Motion efficiency analysis with Performance Score and weekly progress reports</p></div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">📊 Session Data</div>
          <div className="form-group"><label>Exercise</label>
            <select value={form.exercise} onChange={e => setForm(f => ({ ...f, exercise: e.target.value }))}>
              <option value="squat">Squat</option><option value="pushup">Push-Up</option><option value="bicep_curl">Bicep Curl</option><option value="deadlift">Deadlift</option>
            </select>
          </div>
          <div className="grid-2">
            <div className="form-group"><label>Sets Completed</label><input type="number" value={form.sets_completed} onChange={e => setForm(f => ({ ...f, sets_completed: +e.target.value }))} /></div>
            <div className="form-group"><label>Duration (sec)</label><input type="number" value={form.duration_seconds} onChange={e => setForm(f => ({ ...f, duration_seconds: +e.target.value }))} /></div>
          </div>
          <div className="form-group"><label>Reps per Set (comma separated)</label>
            <input value={form.reps_per_set.join(",")} onChange={e => setForm(f => ({ ...f, reps_per_set: e.target.value.split(",").map(Number) }))} placeholder="10,9,10" />
          </div>
          <div className="form-group"><label>Form Scores per Set (0-100)</label>
            <input value={form.form_scores.join(",")} onChange={e => setForm(f => ({ ...f, form_scores: e.target.value.split(",").map(Number) }))} placeholder="82,78,85" />
          </div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button className="btn btn-primary" onClick={analyze} disabled={loading}>{loading ? "Analyzing..." : "🎯 Analyze Session"}</button>
            <button className="btn btn-secondary" onClick={getTips}>💡 Efficiency Tips</button>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {result && (
            <div className="card">
              <div className="card-title">📈 Performance Report</div>
              <div className="score-display">
                <div className="score-number">{result.analysis?.performance_score}</div>
                <div className="score-label">Performance Score</div>
                <span className={`badge ${result.analysis?.grade === "A" ? "badge-green" : result.analysis?.grade === "B" ? "badge-blue" : "badge-yellow"}`} style={{ marginTop: "0.5rem" }}>
                  Grade {result.analysis?.grade} — {result.analysis?.label}
                </span>
              </div>
              <div style={{ marginTop: "1rem" }}>
                {["form_score","consistency_score","completion_score"].map(k => (
                  <div className="stat-row" key={k}>
                    <span className="stat-label">{k.replace(/_/g, " ")}</span>
                    <span className="stat-value">{result.analysis?.breakdown?.[k]}%</span>
                  </div>
                ))}
                <div className="stat-row"><span className="stat-label">Total Reps</span><span className="stat-value">{result.analysis?.total_reps}</span></div>
              </div>
              <div style={{ marginTop: "1rem" }}>
                {result.analysis?.improvements?.map((imp, i) => <div key={i} style={{ fontSize: "0.85rem", marginBottom: "0.3rem" }}>{imp}</div>)}
              </div>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.75rem" }}>
                {result.badges?.map((b, i) => <span key={i} className="badge badge-green">{b}</span>)}
              </div>
            </div>
          )}

          {tips && (
            <div className="card">
              <div className="card-title">💡 Efficiency Tips — {tips.exercise}</div>
              {tips.optimal_angles && Object.entries(tips.optimal_angles).map(([joint, angle]) => (
                <div className="stat-row" key={joint}><span className="stat-label">{joint}</span><span className="stat-value badge badge-blue">{angle}</span></div>
              ))}
              <ul className="feedback-list" style={{ marginTop: "0.75rem" }}>
                {tips.tips?.map((t, i) => <li key={i}>✅ {t}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function SmartGym() {
  const [form, setForm] = useState({ equipment_id: "TM-01", equipment_type: "treadmill", current_resistance: 40, current_speed: 8, heart_rate: 145, calories_burned: 220, session_minutes: 25, user_fitness_level: "intermediate" });
  const [result, setResult] = useState(null);
  const [equipment, setEquipment] = useState(null);
  const [loading, setLoading] = useState(false);

  const monitor = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/smart-gym/monitor`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, current_resistance: +form.current_resistance, current_speed: +form.current_speed, heart_rate: +form.heart_rate, calories_burned: +form.calories_burned, session_minutes: +form.session_minutes }) });
      setResult(await res.json());
    } catch { alert("Backend not running!"); }
    setLoading(false);
  };

  const getEquipment = async () => {
    try {
      const res = await fetch(`${API}/smart-gym/equipment-status`);
      setEquipment(await res.json());
    } catch {}
  };

  return (
    <div>
      <div className="module-header"><h2>📡 Smart Gym Assistant</h2><p>AI + IoT integration for real-time equipment monitoring and auto-adjustment</p></div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">🔌 IoT Sensor Data</div>
          <div className="grid-2">
            {[["Equipment ID","equipment_id","text"],["Heart Rate (bpm)","heart_rate","number"],["Current Resistance","current_resistance","number"],["Speed (km/h)","current_speed","number"],["Calories Burned","calories_burned","number"],["Session (min)","session_minutes","number"]].map(([label,key,type]) => (
              <div className="form-group" key={key}><label>{label}</label>
                <input type={type} value={form[key]} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))} />
              </div>
            ))}
          </div>
          <div className="form-group"><label>Fitness Level</label>
            <select value={form.user_fitness_level} onChange={e => setForm(f => ({ ...f, user_fitness_level: e.target.value }))}>
              <option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option>
            </select>
          </div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button className="btn btn-primary" onClick={monitor} disabled={loading}>{loading ? "Monitoring..." : "📡 Monitor Session"}</button>
            <button className="btn btn-secondary" onClick={getEquipment}>🏋️ Equipment Status</button>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {result && (
            <div className="card">
              <div className="card-title">📊 Live Monitoring Report</div>
              <div className="grid-2" style={{ marginBottom: "1rem" }}>
                <div className="result-box" style={{ textAlign: "center" }}><div className="score-number" style={{ fontSize: "1.6rem" }}>{result.heart_rate_zone?.zone}</div><div className="score-label">HR Zone — {result.heart_rate_zone?.name}</div></div>
                <div className="result-box" style={{ textAlign: "center" }}><div className="score-number" style={{ fontSize: "1.6rem" }}>{result.calories_burned}</div><div className="score-label">Calories Burned</div></div>
              </div>
              <div className="stat-row"><span className="stat-label">Cal/min</span><span className="stat-value">{result.cal_per_minute}</span></div>
              <div className="stat-row"><span className="stat-label">Performance</span><span className="stat-value"><span className="badge badge-green">{result.performance_rating}</span></span></div>
              <div className="stat-row"><span className="stat-label">Rest Needed</span><span className="stat-value"><span className={`badge ${result.rest_recommended ? "badge-red" : "badge-green"}`}>{result.rest_recommended ? "Yes" : "No"}</span></span></div>
              <ul className="feedback-list" style={{ marginTop: "0.75rem" }}>
                {result.recommendations?.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}

          {equipment && (
            <div className="card">
              <div className="card-title">🏋️ Equipment Status</div>
              <div className="grid-3" style={{ marginBottom: "1rem" }}>
                <div className="result-box" style={{ textAlign: "center" }}><div className="score-number" style={{ fontSize: "1.6rem", color: "var(--green)" }}>{equipment.available}</div><div className="score-label">Available</div></div>
                <div className="result-box" style={{ textAlign: "center" }}><div className="score-number" style={{ fontSize: "1.6rem", color: "var(--yellow)" }}>{equipment.in_use}</div><div className="score-label">In Use</div></div>
                <div className="result-box" style={{ textAlign: "center" }}><div className="score-number" style={{ fontSize: "1.6rem", color: "var(--red)" }}>{equipment.maintenance}</div><div className="score-label">Maintenance</div></div>
              </div>
              {equipment.equipment?.map((e, i) => (
                <div className="stat-row" key={i}>
                  <span className="stat-value">{e.id} — {e.type}</span>
                  <span className={`badge ${e.status === "available" ? "badge-green" : e.status === "in_use" ? "badge-yellow" : "badge-red"}`}>{e.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function GymRecommender() {
  const [form, setForm] = useState({ user_id: "user1", location: "pune", fitness_goal: "muscle_gain", fitness_level: "beginner", budget_inr: 2000, preferred_timing: "morning", equipment_preference: "gym", past_programs: [] });
  const [gyms, setGyms] = useState(null);
  const [program, setProgram] = useState(null);
  const [challenges, setChallenges] = useState(null);
  const [loading, setLoading] = useState(false);

  const getGyms = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/gym-recommender/recommend-gyms`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, budget_inr: +form.budget_inr }) });
      setGyms(await res.json());
    } catch { alert("Backend not running!"); }
    setLoading(false);
  };

  const getProgram = async () => {
    try {
      const res = await fetch(`${API}/gym-recommender/recommend-program`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ fitness_goal: form.fitness_goal, fitness_level: form.fitness_level, days_per_week: 3, equipment: "full_gym" }) });
      setProgram(await res.json());
    } catch {}
  };

  const getChallenges = async () => {
    try {
      const res = await fetch(`${API}/gym-recommender/challenges`);
      setChallenges(await res.json());
    } catch {}
  };

  return (
    <div>
      <div className="module-header"><h2>🗺️ Gym Recommender & Planner</h2><p>AI-powered gym recommendations, workout programs, and fitness challenges near you</p></div>
      <div className="grid-2">
        <div className="card">
          <div className="card-title">⚙️ Your Preferences</div>
          <div className="grid-2">
            <div className="form-group"><label>Location</label><input value={form.location} onChange={e => setForm(f => ({ ...f, location: e.target.value }))} placeholder="pune / mumbai" /></div>
            <div className="form-group"><label>Budget (₹/month)</label><input type="number" value={form.budget_inr} onChange={e => setForm(f => ({ ...f, budget_inr: e.target.value }))} /></div>
          </div>
          <div className="grid-2">
            <div className="form-group"><label>Fitness Goal</label>
              <select value={form.fitness_goal} onChange={e => setForm(f => ({ ...f, fitness_goal: e.target.value }))}>
                <option value="weight_loss">Weight Loss</option><option value="muscle_gain">Muscle Gain</option><option value="endurance">Endurance</option><option value="flexibility">Flexibility</option>
              </select>
            </div>
            <div className="form-group"><label>Fitness Level</label>
              <select value={form.fitness_level} onChange={e => setForm(f => ({ ...f, fitness_level: e.target.value }))}>
                <option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option>
              </select>
            </div>
          </div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <button className="btn btn-primary" onClick={getGyms} disabled={loading}>{loading ? "Finding..." : "🗺️ Find Gyms"}</button>
            <button className="btn btn-secondary" onClick={getProgram}>📋 Get Program</button>
            <button className="btn btn-secondary" onClick={getChallenges}>🏆 Challenges</button>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {gyms && (
            <div className="card">
              <div className="card-title">🏋️ Top Gym Picks Near You</div>
              {gyms.top_picks?.map((g, i) => (
                <div key={i} className="result-box" style={{ marginBottom: "0.75rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontWeight: 700 }}>#{i+1} {g.name}</span>
                    <span className="badge badge-green">⭐ {g.rating}</span>
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text2)", marginTop: "0.35rem" }}>{g.area} · ₹{g.monthly_fee}/month · {g.timing}</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginTop: "0.5rem" }}>
                    {g.facilities?.map(f => <span key={f} className="badge badge-blue" style={{ fontSize: "0.7rem" }}>{f}</span>)}
                  </div>
                </div>
              ))}
              <p style={{ fontSize: "0.8rem", color: "var(--text2)" }}>💡 {gyms.tip}</p>
            </div>
          )}
        </div>
      </div>

      {program && (
        <div className="card" style={{ marginTop: "1.5rem" }}>
          <div className="card-title">📋 {program.recommended_program?.name}</div>
          <p style={{ color: "var(--text2)", fontSize: "0.875rem", marginBottom: "1rem" }}>{program.recommended_program?.description}</p>
          <div className="grid-3">
            {program.recommended_program?.schedule?.map((day, i) => (
              <div key={i} className="result-box">
                <div style={{ fontWeight: 700, color: "var(--accent)", marginBottom: "0.5rem" }}>{day.day} — {day.focus}</div>
                <ul style={{ paddingLeft: "1rem", fontSize: "0.8rem", color: "var(--text2)" }}>
                  {day.exercises?.map((ex, j) => <li key={j}>{ex}</li>)}
                </ul>
              </div>
            ))}
          </div>
          <div style={{ marginTop: "1rem" }}>
            <span className="badge badge-yellow">🥗 {program.recommended_program?.nutrition_tip}</span>
            <span className="badge badge-green" style={{ marginLeft: "0.5rem" }}>🎯 {program.recommended_program?.expected_result}</span>
          </div>
        </div>
      )}

      {challenges && (
        <div style={{ marginTop: "1.5rem" }}>
          <div style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "1rem" }}>🏆 Active Fitness Challenges</div>
          <div className="grid-3">
            {challenges.challenges?.map(c => (
              <div key={c.id} className="card">
                <div className="card-title">{c.name}</div>
                <div className="stat-row"><span className="stat-label">Duration</span><span className="stat-value">{c.duration_days} days</span></div>
                <div className="stat-row"><span className="stat-label">Difficulty</span><span className={`badge ${c.difficulty === "beginner" ? "badge-green" : "badge-yellow"}`}>{c.difficulty}</span></div>
                <p style={{ fontSize: "0.8rem", color: "var(--text2)", marginTop: "0.5rem" }}>📌 {c.daily_target}</p>
                <button className="btn btn-primary" style={{ width: "100%", marginTop: "0.75rem", fontSize: "0.8rem" }}>Join Challenge</button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
