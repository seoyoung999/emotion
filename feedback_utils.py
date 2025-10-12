# feedback_utils.py

import json, os
from datetime import datetime

FEEDBACK_PATH = "data/feedback.json"

def save_feedback(user_id, challenge_title, status, interest, satisfaction, emotion_after):
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(FEEDBACK_PATH):
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append({
        "user_id": user_id,
        "challenge_title": challenge_title,
        "status": status,
        "interest": interest,
        "satisfaction": satisfaction,
        "emotion_after": emotion_after,
        "timestamp": datetime.now().isoformat()
    })

    with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
