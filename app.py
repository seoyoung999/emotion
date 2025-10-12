# app.py

from flask import Flask, render_template, request, session, jsonify
from datetime import datetime, timedelta
from model import calculate_total_score
from recommend import recommend_all_challenges
from feedback_utils import save_feedback
from chatbot import get_chatbot_response

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USER_ID = "user123"

# 감정 점수 기반 감정 상태 텍스트 분류
def classify_emotion_by_score(scores):
    avg = (scores['mood'] + scores['sleep'] + scores['activity'] + scores['text_score']) / 4
    if avg <= 3:
        return "매우 나쁨"
    elif avg <= 5:
        return "나쁨"
    elif avg <= 7:
        return "보통"
    elif avg <= 8.5:
        return "긍정적"
    else:
        return "매우 긍정적"

@app.route('/')
def home():
    last_visit = session.get('last_visit')
    now = datetime.now()

    if not last_visit:
        session['bad_count'] = 0
        session['feedbacks'] = []
    else:
        try:
            last_time = datetime.strptime(last_visit, "%Y-%m-%d %H:%M:%S")
            if now - last_time > timedelta(minutes=10):
                session['bad_count'] = 0
                session['feedbacks'] = []
        except Exception:
            session['bad_count'] = 0
            session['feedbacks'] = []

    session['last_visit'] = now.strftime("%Y-%m-%d %H:%M:%S")

    bad_count = session.get('bad_count', 0)
    show_chatbot = bad_count >= 5
    return render_template('index.html', show_chatbot=show_chatbot)

@app.route('/analyze', methods=['POST'])
def analyze():
    mood = int(request.form['mood'])
    sleep = int(request.form['sleep'])
    activity = int(request.form['activity'])
    feeling_text = request.form['feeling_text']
    interest = request.form['interest']

    scores, text_emotion = calculate_total_score(mood, sleep, activity, feeling_text)
    status_kor = classify_emotion_by_score(scores)

    bad_score = scores['text_score'] <= 5
    bad_count = session.get('bad_count', 0)
    if bad_score:
        bad_count += 1
    else:
        bad_count = 0
    session['bad_count'] = bad_count

    feedbacks = session.get('feedbacks', [])
    all_recommendations = recommend_all_challenges(feeling_text, interest, feedbacks)

    selected = all_recommendations[0]

    return f"""
    <link rel="stylesheet" href="/static/style.css">
    <div class="result-card">
      <h2>🌈 감정 상태: <span style='color:#5c7cfa'>{status_kor}</span></h2>
      <h3>🎯 추천 챌린지: {selected['title']}</h3>
      <p>{selected['description']}</p>
      <p><a href="{selected.get('youtube', '#')}" target="_blank" rel="noopener noreferrer">▶️ 유튜브 영상 보기</a></p>
      <p><a href="{selected.get('blog', '#')}" target="_blank" rel="noopener noreferrer">✍️ 관련 블로그 보기</a></p>
      <form action="/feedback" method="post">
        <input type="hidden" name="user_id" value="{USER_ID}">
        <input type="hidden" name="status" value="{status_kor}">
        <input type="hidden" name="interest" value="{interest}">
        <input type="hidden" name="challenge_title" value="{selected['title']}">
        <p>📝 챌린지 만족도 (1~5): <input type="number" name="satisfaction" min="1" max="5" step="1" required></p>
        <p>📈 감정 변화 (예: 매우 긍정적): <input type="text" name="emotion_after" required></p>
        <button type="submit">피드백 제출</button>
      </form>
      <br><a href="/">🔁 다시 분석하기</a>
    </div>
    """

@app.route('/feedback', methods=['POST'])
def feedback():
    user_id = request.form['user_id']
    challenge_title = request.form['challenge_title']
    status = request.form['status']
    interest = request.form['interest']
    satisfaction = int(request.form['satisfaction'])

    if satisfaction not in [1, 2, 3, 4, 5]:
        return """
        <link rel="stylesheet" href="/static/style.css">
        <div class="result-card">
            <h2>⚠️ 유효하지 않은 만족도입니다.</h2>
            <p>1부터 5 사이의 숫자만 입력해 주세요.</p>
            <a href="/">돌아가기</a>
        </div>
        """

    emotion_after = request.form['emotion_after']
    save_feedback(user_id, challenge_title, status, interest, satisfaction, emotion_after)

    # 세션 내 피드백 저장
    feedbacks = session.get('feedbacks', [])
    feedbacks.append({
        "challenge_title": challenge_title,
        "satisfaction": satisfaction
    })
    session['feedbacks'] = feedbacks

    return f"""
    <link rel="stylesheet" href="/static/style.css">
    <div class="result-card">
      <h2>✅ 피드백이 저장되었습니다!</h2>
      <p>감사합니다. 앞으로 더 맞춤형 추천을 제공할게요 😊</p>
      <a href="/">🔁 다시 분석하러 가기</a>
    </div>
    """

@app.route('/submit_bad_score', methods=['POST'])
def submit_bad_score():
    bad_score = int(request.form.get('bad_score', 0))
    bad_count = session.get('bad_count', 0)

    if bad_score > 0:  # 나쁨 지수 감지 시 카운트 증가
        bad_count += 1
        session['bad_count'] = bad_count

    return jsonify({'bad_count': bad_count})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message', '').strip()

    if user_input == '':
        session_state = {}
    else:
        session_state = session.get('chatbot_state', {})

    response, session_state = get_chatbot_response(user_input, session_state)
    session['chatbot_state'] = session_state

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
