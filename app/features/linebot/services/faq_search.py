import json
import numpy as np
from bs4 import BeautifulSoup
from app.features.linebot.services.openai_client import get_openai_reply, client
from app.features.linebot.services.line_client import send_line_reply

# 🔹 ユーザーごとの会話履歴
USER_CONVERSATIONS = {}

def get_embedding(text: str) -> list:
    """
    OpenAI APIでテキストをEmbeddingに変換する
    """
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    """
    コサイン類似度を計算
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def clean_html(raw_html: str) -> str:
    """
    HTMLタグを除去してテキストのみを返す
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=' ', strip=True)

def search_faq(user_message: str, user_info: dict, reply_token: str) -> str:
    """
    FAQデータを検索し、ユーザーの履歴を考慮して回答を生成
    """
    try:
        user_id = user_info.get('id')

        if not user_id:
            return "会員登録がまだ完了していないようです。ぜひ会員登録をして、すべての機能をご利用ください！😊"

        user_nickname = user_info.get('nickname', 'ユーザー')
        user_sex = user_info.get('sex', 'NULL')

        # ✅ `YES` の場合、履歴を削除し、削除後の履歴をログに出力
        if user_message.upper() == "リセット":
            if user_id in USER_CONVERSATIONS:
                USER_CONVERSATIONS[user_id].clear()  # 🔹 キーを保持しつつ内容をクリア
                del USER_CONVERSATIONS[user_id]  # 🔹 キーごと完全削除

            print(f"🗑 {user_id} の履歴を削除しました")
            send_line_reply(reply_token, "ありがとうございました。またお気軽に質問してくださいね😊")
            return  

        # ✅ 履歴をログに出力（デバッグ用）
        print(f"🔍 {user_id} の現在の履歴: {USER_CONVERSATIONS.get(user_id, '履歴なし')}")

        # ✅ 履歴を保存（存在しない場合は作成）
        if user_id not in USER_CONVERSATIONS:
            USER_CONVERSATIONS[user_id] = []

        # ✅ 5往復（10発言）以上なら古いものから削除
        while len(USER_CONVERSATIONS[user_id]) >= 10:
            USER_CONVERSATIONS[user_id].pop(0)

        USER_CONVERSATIONS[user_id].append({"user": user_message})

        # ✅ `microcms_faq_embeddings.json` からFAQデータを読み込む
        with open('app/data/microcms_faq_embeddings.json', 'r') as f:
            faqs = json.load(f)

        # ✅ 性別でFAQをフィルタリング
        matched_faqs = [
            faq for faq in faqs 
            if faq['sex'] == user_sex or faq['sex'] == 'NULL'
        ]

        # ✅ ユーザーの質問に最も近いFAQを **複数** 取得（スコア0.85以上）
        user_embedding = get_embedding(user_message)
        relevant_faqs = []
        for faq in matched_faqs:
            faq_embedding = faq['embedding']
            similarity = cosine_similarity(user_embedding, faq_embedding)
            if similarity > 0.85:  # 類似度が0.85以上のものを収集
                relevant_faqs.append((faq, similarity))

        # ✅ 類似度の高い順にソート（最も関連性の高いFAQから順に処理）
        relevant_faqs.sort(key=lambda x: x[1], reverse=True)

        # ✅ 過去の会話履歴を取得（最新5~10ターン分）
        conversation_history = "\n".join(
            [f"ユーザー: {conv['user']}" if 'user' in conv else f"ボット: {conv['bot']}" 
            for conv in USER_CONVERSATIONS[user_id][-10:]]
        ) if USER_CONVERSATIONS[user_id] else "履歴なし"

        # ✅ FAQが1つ以上見つかった場合、それらを **要約・統合**
        if relevant_faqs:
            cleaned_faq_answers = "\n".join(
                [clean_html(faq['answer']) for faq, _ in relevant_faqs]
            )

            system_prompt = (
                f"以下はユーザー {user_nickname} との最近の会話履歴です。\n"
                f"---\n"
                f"{conversation_history}\n"
                f"---\n"
                f"ユーザーの最新の質問: {user_message}\n"
                f"以下のFAQの情報を **簡潔かつ手短に要約** して、分かりやすい回答を作成してください。\n"
                f"FAQの内容:\n"
                f"{cleaned_faq_answers}"
            )

            reply = get_openai_reply(user_message, system_prompt)

        # ✅ FAQで見つからなかった場合は、履歴を考慮して OpenAI に質問
        else:
            system_prompt = (
                f"以下はユーザー {user_nickname} との最近の会話履歴です。\n"
                f"---\n"
                f"{conversation_history}\n"
                f"---\n"
                f"ユーザーの最新の質問: {user_message}\n"
                f"過去の会話を踏まえて、自然な返答をしてください。"
                f"接客サービスの内容に関係なさそうな場合はその件には答えなくていいです。"
                f"相手の質問が曖昧な場合は聞き返して下さい。"
                f"内容について曖昧な場合は答えないでサポートへ問い合わせを促して下さい。"
                f"雑な回答は避け、サポートへの問い合わせを促して下さい。"
                f"基本的に相手は弊社のキャストです。よって、サービスについての質問しかしてこない前提です。"
            )

            reply = get_openai_reply(user_message, system_prompt)

        # ✅ 履歴に Bot の回答も追加
        USER_CONVERSATIONS[user_id].append({"bot": reply})

        # ✅ LINEへメッセージ送信
        send_line_reply(reply_token, reply)

        return reply

    except Exception as e:
        print(f"❌ FAQ検索中にエラー: {e}")
        return "FAQ検索中にエラーが発生しました。"
