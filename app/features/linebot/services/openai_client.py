from openai import OpenAI
from app.core.config import OPENAI_API_KEY

# OpenAIクライアント初期化
client = OpenAI(api_key=OPENAI_API_KEY)

def get_openai_reply(user_message: str, system_prompt: str = "あなたは親切なアシスタントです。") -> str:
    """
    OpenAI APIを使用して動的な返答を生成
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "申し訳ありません、エラーが発生しました。"
