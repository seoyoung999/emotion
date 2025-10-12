# chatbot.py

import os
import pandas as pd

# PHQ-9 질문 리스트
PHQ9_QUESTIONS = [
    "1. 😞 거의 매일 우울하거나 기분이 처졌던 날이 있었나요?",
    "2. 😐 거의 매일 흥미나 즐거움이 줄어든 적이 있었나요?",
    "3. 😴 수면에 문제가 있었나요? (잠이 너무 많거나 너무 적음)",
    "4. 😩 피곤하거나 기운이 없다고 느낀 적이 있었나요?",
    "5. 🍽️ 식욕이 줄었거나 지나치게 늘었던 적이 있었나요?",
    "6. 💔 스스로가 실패자라고 느끼거나 자신과 가족을 실망시켰다고 느낀 적이 있었나요?",
    "7. 🤯 집중하는 데 어려움이 있었나요? (예: 책 읽기, TV 시청 등)",
    "8. 🌀 너무 느리거나, 반대로 안절부절못한 적이 있었나요?",
    "9. ⚠️ 죽고 싶다는 생각이나 자해를 고민한 적이 있었나요?"
]

def load_hospitals_from_csv():
    file_path = os.path.join("data", "hospitals.xlsx")

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        hospitals = []
        for _, row in df.iterrows():
            hospitals.append({
                "name": row.get("의료기관명", ""),
                "address": row.get("도로명주소", ""),
                "phone": row.get("전화번호", "")
            })
        return hospitals if hospitals else [{"name": "정보를 불러올 수 없습니다", "address": "", "phone": ""}]
    except Exception as e:
        print("엑셀 파일 읽기 실패:", e)
        return [{"name": "정보를 불러올 수 없습니다", "address": "", "phone": ""}]

def get_chatbot_response(user_input, session_state):
    step = session_state.get('step', 0)

    if step == 0:
        session_state['step'] = 1
        session_state['phq9_scores'] = []
        return (
            "**🧠 우울증 자가진단(PHQ-9)을 시작합니다.**\n\n"
            "각 문항에 대해 아래 숫자 중 하나로 응답해 주세요:\n"
            "```\n"
            "0: 전혀 아님\n"
            "1: 며칠 동안\n"
            "2: 일주일 이상\n"
            "3: 거의 매일\n"
            "```\n\n"
            f"{PHQ9_QUESTIONS[0]}",
            session_state
        )

    elif 1 <= step <= 9:
        try:
            score = int(user_input)
            if score not in [0, 1, 2, 3]:
                raise ValueError()
            session_state['phq9_scores'].append(score)
        except:
            return ("⚠️ 숫자 0, 1, 2, 3 중 하나로만 입력해 주세요. 예: `2`", session_state)

        if step < 9:
            session_state['step'] += 1
            return (PHQ9_QUESTIONS[step], session_state)
        else:
            total_score = sum(session_state['phq9_scores'])
            session_state['step'] = 10

            if total_score >= 10:
                hospitals = load_hospitals_from_csv()
                hospital_info = (
                    f"📊 **총점: {total_score}점** - 우울 증상이 *약간 심한 수준 이상*입니다.\n\n"
                    "🏥 **가까운 병원 정보:**\n"
                )
                for h in hospitals[:5]:
                    hospital_info += (
                        f"- **{h['name']}**\n"
                        f"  📍 {h['address']}\n"
                        f"  ☎️ {h['phone']}\n\n"
                    )
                hospital_info += "🔗 더 많은 병원은 [여기서 확인하세요](https://www.goodhosrank.com/hospital/index.php)."
                return (hospital_info, session_state)
            else:
                return (
                    f"📊 **총점: {total_score}점** - 현재 우울 증상은 심하지 않은 것으로 보입니다.\n\n"
                    "하지만 필요 시 전문가의 도움을 받는 것도 좋은 방법입니다. 🌱",
                    session_state
                )

    else:
        return ("💬 다른 도움이 필요하시면 언제든지 말씀해 주세요.", session_state)
