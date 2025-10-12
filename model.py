# model.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

MODEL_NAME = "beomi/kcbert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

labels = ['Negative', 'Neutral', 'Positive']
emotion_map = {'Negative': 0, 'Neutral': 1, 'Positive': 2}

def analyze_text_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    scores = probs.detach().numpy()[0]
    max_idx = np.argmax(scores)
    return labels[max_idx], scores[max_idx]

def calculate_total_score(mood, sleep, activity, feeling_text):
    text_emotion, _ = analyze_text_emotion(feeling_text)
    text_score = emotion_map.get(text_emotion, 1) * 5  # 0~10점

    sleep_adj = max(sleep, 4)

    combined_score = (
        mood * 0.35 +
        sleep_adj * 0.15 +
        activity * 0.2 +
        text_score * 0.3
    )

    # 부정 감정 상한선
    if text_emotion == 'Negative' and combined_score > 6.0:
        combined_score = 6.0

    total_scores = {
        'mood': mood,
        'sleep': sleep_adj,
        'activity': activity,
        'text_score': text_score,
        'combined_score': combined_score
    }
    return total_scores, text_emotion
