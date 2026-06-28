import { useState } from "react";

const API = "http://localhost:8000/api";

export default function VirtualBuddy() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "👋 Hey! I'm your AI Gym Buddy. Ask me anything about fitness, tell me how you're feeling, or just chat! 💪" }
  ]);
  const [input, setInput] = useState("");
  const [context, setContext] = useState("general");
  const [loading, setLoading] = useState(false);
  const [quote, setQuote] = useState(null);
  const [emotion, setEmotion] = useState(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: "user", text: userMsg }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/virtual-buddy/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "user1", message: userMsg, context })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "bot", text: `${data.emoji_mood} ${data.response}` }]);
      setEmotion(data.sentiment);
    } catch {
      setMessages(prev => [...prev, { role: "bot", text: "⚠️ Could not connect to server. Make sure the backend is running!" }]);
    }
    setLoading(false);
  };

  const fetchQuote = async () => {
    try {
      const res = await fetch(`${API}/virtual-buddy/daily-quote`);
      const data = await res.json();
      setQuote(data);
    } catch { setQuote({ quote: "Keep pushing — every rep counts!", author: "AI Buddy" }); }
  };

  return (
    <div>
      <div className="module-header">
        <h2>🤖 Virtual Gym Buddy</h2>
        <p>Your AI companion for motivation, emotional support, and fitness Q&A</p>
      </div>

      <div className="grid-2">
        {/* Chat */}
        <div className="card">
          <div className="card-title">💬 Chat with your Buddy</div>

          <div className="form-group">
            <label>Context</label>
            <select value={context} onChange={e => setContext(e.target.value)}>
              <option value="general">General</option>
              <option value="pre_workout">Pre-Workout</option>
              <option value="post_workout">Post-Workout</option>
            </select>
          </div>

          <div className="chat-window">
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}`}>{m.text}</div>
            ))}
            {loading && (
              <div className="chat-msg bot">
                <div className="loading"><div className="spinner" /> Buddy is thinking...</div>
              </div>
            )}
          </div>

          <div className="chat-input-row">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendMessage()}
              placeholder="Ask anything or tell me how you feel..."
            />
            <button className="btn btn-primary" onClick={sendMessage} disabled={loading}>Send</button>
          </div>

          {emotion && (
            <div style={{ marginTop: "0.75rem" }}>
              <span className={`badge ${emotion === "positive" ? "badge-green" : emotion === "negative" ? "badge-red" : "badge-yellow"}`}>
                Detected mood: {emotion}
              </span>
            </div>
          )}
        </div>

        {/* Daily Quote + FAQ hints */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div className="card">
            <div className="card-title">🌟 Daily Motivation Quote</div>
            <button className="btn btn-secondary" onClick={fetchQuote} style={{ marginBottom: "1rem" }}>
              Get Today's Quote
            </button>
            {quote && (
              <div className="result-box">
                <p style={{ fontSize: "1rem", fontStyle: "italic", color: "var(--text)", lineHeight: 1.6 }}>
                  "{quote.quote}"
                </p>
                <p style={{ marginTop: "0.5rem", color: "var(--text2)", fontSize: "0.8rem" }}>— {quote.author}</p>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-title">💡 Ask me about...</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
              {["How many calories?", "Best exercise for weight loss?", "How much protein?", "Importance of sleep", "Should I take supplements?", "How to stay motivated?"].map(q => (
                <button key={q} className="btn btn-secondary" style={{ fontSize: "0.78rem", padding: "0.4rem 0.8rem" }}
                  onClick={() => { setInput(q); }}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
