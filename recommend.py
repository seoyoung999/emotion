# recommend.py

from sentence_transformers import SentenceTransformer, util
import torch
import os
import json
import random

# 모델 로드
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# 챌린지 데이터 로딩
with open(os.path.join("static", "challenges_50.json"), "r", encoding="utf-8") as f:
    challenges = json.load(f)

# 챌린지 태그 임베딩 사전 계산
challenge_embeddings = model.encode([c['tags'] for c in challenges], convert_to_tensor=True)

def recommend_challenge(feeling_text, interest, top_k=5):
    query_text = f"{feeling_text} {interest}"
    user_embedding = model.encode(query_text, convert_to_tensor=True)

    cosine_scores = util.cos_sim(user_embedding, challenge_embeddings)[0]
    top_results = torch.topk(cosine_scores, k=top_k)
    top_indices = top_results.indices.tolist()

    selected_idx = random.choice(top_indices)
    return challenges[selected_idx]

def recommend_all_challenges(feeling_text, interest, feedbacks=None):
    query_text = f"{feeling_text} {interest}"
    user_embedding = model.encode(query_text, convert_to_tensor=True)

    cosine_scores = util.cos_sim(user_embedding, challenge_embeddings)[0]
    scores_and_idx = list(zip(cosine_scores.tolist(), range(len(challenges))))

    # 👇 피드백 기반 가중치 조정
    if feedbacks:
        for i, (score, idx) in enumerate(scores_and_idx):
            challenge_title = challenges[idx]['title']
            for f in feedbacks:
                if f['challenge_title'] == challenge_title and f['satisfaction'] < 3:
                    scores_and_idx[i] = (score - 0.2, idx)
                    break

    scores_and_idx.sort(key=lambda x: x[0], reverse=True)
    top_k = 10
    top_indices = [idx for _, idx in scores_and_idx[:top_k]]
    return [challenges[i] for i in top_indices]
