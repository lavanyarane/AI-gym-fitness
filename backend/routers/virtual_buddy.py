"""
Module 5: Virtual Gym Buddy (AI Chat Companion)
Motivates users, tracks emotional states, provides personalized guidance
using sentiment analysis and conversational AI.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────
class ChatMessage(BaseModel):
    user_id: str
    message: str
    context: Optional[str] = "general"   # "pre_workout" / "post_workout" / "general"

class EmotionData(BaseModel):
    user_id: str
    message: str


# ──────────────────────────────────────────────
# Sentiment / Emotion Analysis
# ──────────────────────────────────────────────
POSITIVE_KEYWORDS = [
    "great", "awesome", "amazing", "good", "happy", "motivated", "strong",
    "energetic", "pumped", "ready", "excited", "love", "best", "proud",
    "crushed", "killed", "nailed", "completed", "finished"
]
NEGATIVE_KEYWORDS = [
    "tired", "exhausted", "lazy", "skip", "rest", "sick", "pain", "hurt",
    "demotivated", "cant", "cannot", "won't", "sad", "stressed", "overwhelmed",
    "no energy", "bad", "terrible", "hate", "worst", "give up", "quit"
]
NEUTRAL_KEYWORDS  = ["okay", "fine", "normal", "average", "maybe", "perhaps"]

RESPONSES = {
    "positive": {
        "pre_workout":  [
            "🔥 That energy is EVERYTHING! Let's turn it into a legendary session!",
            "⚡ You're already winning mentally — now let's crush it physically!",
            "💪 Love this attitude! Your body is going to thank you for this!"
        ],
        "post_workout": [
            "🏆 Absolute beast mode! You showed up and delivered — that's champion behavior!",
            "🌟 Look at you GO! Another session in the books — you're unstoppable!",
            "✨ That's what consistency looks like. Proud of you!"
        ],
        "general": [
            "🎯 Your mindset is on point! Keep bringing this energy every day!",
            "🚀 This positivity is contagious — keep it rolling!",
            "💫 Love your energy today! How can I help you channel it?"
        ]
    },
    "negative": {
        "pre_workout": [
            "🤗 Feeling low energy today? That's completely okay. Even a 15-min light session will shift your mood — I promise!",
            "💙 Listen to your body, but don't confuse tiredness with laziness. A warm-up might be all you need.",
            "🌱 Some days are harder. Want to try a shorter, gentler workout today instead of skipping entirely?"
        ],
        "post_workout": [
            "❤️ Hey, any workout counts — even the tough ones where you wanted to quit. You still showed up!",
            "🌟 Rough session? That's okay. Recovery is part of the journey. Rest well tonight.",
            "💪 The fact that you showed up when you didn't want to? That's REAL discipline."
        ],
        "general": [
            "💙 I'm here for you. What's going on? Want to talk about it or should we plan something easy for today?",
            "🤗 Bad days are part of the journey. What's one tiny thing we can do to feel just 10% better?",
            "🌱 It's okay to not be okay. Rest, recharge — then we come back stronger."
        ]
    },
    "neutral": {
        "pre_workout":  ["😊 Ready to get started? Let's make today's session count!"],
        "post_workout": ["✅ Good job showing up! How did it feel?"],
        "general":      ["👋 How can I help you today? Ask me anything about your fitness!"]
    }
}

FITNESS_QA = {
    "how many calories": "Your daily calorie target depends on your goal! Use the Diet module to get a personalized number based on your BMI and activity level. 🥗",
    "best exercise":     "The best exercise is the one you'll actually do consistently! For muscle: compound lifts (squats, deadlifts, bench). For fat loss: HIIT + strength training. 💪",
    "how to lose weight":"Calorie deficit + strength training is the proven formula. Aim for 500 kcal deficit/day and lift 3x/week. Track your meals in the Diet module! 🎯",
    "rest day":          "Rest days are NOT optional — they're when your muscles actually grow! Aim for 1–2 rest days per week, with light walks or yoga. 😴",
    "protein":           "General guideline: 1.6–2.2g protein per kg of bodyweight for muscle building. For a 65kg person, that's ~105–143g/day. 🥩",
    "motivation":        "Motivation is temporary — discipline is permanent. Build a routine, track your progress, and remember your WHY. I'm here to nudge you every day! 🔥",
    "warm up":           "Always warm up for 5–10 min! Light cardio + dynamic stretches prevents injury and improves performance. Never skip it! 🏃",
    "sleep":             "Sleep is your #1 recovery tool! 7–9 hours per night optimizes muscle repair, hormone balance, and mental focus. 💤",
    "supplement":        "Focus on food first. If needed: whey protein, creatine, and vitamin D are the most evidence-backed supplements. Consult a doctor before starting. 💊",
    "water":             "Drink at least 35ml per kg of bodyweight daily. So for 65kg: ~2.3 liters. More on workout days! 💧"
}


def analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment analysis."""
    text_lower = text.lower()
    pos_count  = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    neg_count  = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return "neutral"


def get_quick_answer(message: str) -> Optional[str]:
    """Check if message matches a FAQ topic."""
    msg_lower = message.lower()
    for keyword, answer in FITNESS_QA.items():
        if keyword in msg_lower:
            return answer
    return None


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@router.post("/chat")
def chat(msg: ChatMessage):
    """Main conversational endpoint for the Virtual Gym Buddy."""
    sentiment = analyze_sentiment(msg.message)
    context   = msg.context or "general"

    # Check for FAQ match first
    quick_ans = get_quick_answer(msg.message)
    if quick_ans:
        return {
            "user_id":   msg.user_id,
            "sentiment": sentiment,
            "response":  quick_ans,
            "context":   context,
            "emoji_mood": "🤔"
        }

    # Get emotion-based response
    import random
    response_pool = RESPONSES.get(sentiment, RESPONSES["neutral"])
    context_pool  = response_pool.get(context, response_pool.get("general", ["How can I help you? 😊"]))
    response      = random.choice(context_pool)

    mood_emoji = {"positive": "😄", "negative": "💙", "neutral": "😊"}.get(sentiment, "😊")

    return {
        "user_id":    msg.user_id,
        "sentiment":  sentiment,
        "response":   response,
        "context":    context,
        "emoji_mood": mood_emoji,
        "follow_up":  "Want to log today's workout, check your diet plan, or get a motivational quote? 🎯"
    }


@router.post("/analyze-emotion")
def analyze_emotion(data: EmotionData):
    """Analyze the emotional state from user's message."""
    sentiment = analyze_sentiment(data.message)
    text_lower = data.message.lower()

    emotions = {
        "motivated":    any(w in text_lower for w in ["pumped", "ready", "motivated", "excited"]),
        "tired":        any(w in text_lower for w in ["tired", "exhausted", "drained", "no energy"]),
        "stressed":     any(w in text_lower for w in ["stressed", "overwhelmed", "anxious", "pressure"]),
        "happy":        any(w in text_lower for w in ["happy", "great", "amazing", "awesome"]),
        "demotivated":  any(w in text_lower for w in ["cant", "quit", "give up", "hate", "skip"]),
    }

    detected = [e for e, v in emotions.items() if v]

    recommendations = []
    if "tired" in detected:
        recommendations.append("Consider a lighter session — yoga, walking, or stretching")
    if "stressed" in detected:
        recommendations.append("Exercise is great for stress! Even 20 min will help")
    if "demotivated" in detected:
        recommendations.append("Watch your progress stats — you've come further than you think!")
    if "motivated" in detected:
        recommendations.append("Perfect time for a high-intensity session — make it count!")
    if not recommendations:
        recommendations.append("You seem balanced — have a great workout!")

    return {
        "user_id":        data.user_id,
        "overall_sentiment": sentiment,
        "detected_emotions": detected if detected else ["neutral"],
        "recommendations":   recommendations,
        "wellness_score":    70 if sentiment == "neutral" else 90 if sentiment == "positive" else 40
    }


@router.get("/daily-quote")
def get_daily_quote():
    """Get an AI-curated motivational fitness quote."""
    import random, datetime
    quotes = [
        {"quote": "The only bad workout is the one that didn't happen.", "author": "Unknown"},
        {"quote": "Take care of your body. It's the only place you have to live.", "author": "Jim Rohn"},
        {"quote": "Strength does not come from physical capacity. It comes from an indomitable will.", "author": "Gandhi"},
        {"quote": "The pain you feel today will be the strength you feel tomorrow.", "author": "Unknown"},
        {"quote": "Don't wish for it. Work for it.", "author": "Unknown"},
        {"quote": "Your body can stand almost anything. It's your mind you have to convince.", "author": "Unknown"},
        {"quote": "Fitness is not about being better than someone else. It's about being better than you used to be.", "author": "Unknown"},
    ]
    day_index = datetime.date.today().toordinal() % len(quotes)
    q = quotes[day_index]
    return {
        "quote":  q["quote"],
        "author": q["author"],
        "date":   str(datetime.date.today())
    }
