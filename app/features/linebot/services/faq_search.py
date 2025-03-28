import json
import numpy as np
import logging
import time
import os
import traceback
from bs4 import BeautifulSoup
from app.features.linebot.services.openai_client import get_openai_reply, client
from app.features.linebot.services.line_client import send_line_reply
from app.core.config import is_aws_environment

# ロガーの設定
logger = logging.getLogger("faq_search")

# ユーザーごとの会話履歴
USER_CONVERSATIONS = {}

# FAQデータファイルのパス
FAQ_DATA_PATH = 'app/data/microcms_faq_embeddings.json'

def get_embedding(text: str) -> list:
    """
    OpenAI APIでテキストをEmbeddingに変換する
    """
    start_time = time.time()
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embedding = response.data[0].embedding
        logger.debug(f"Embedding取得完了: 処理時間={time.time() - start_time:.2f}秒")
        return embedding
    except Exception as e:
        logger.error(f"Embedding取得中にエラー: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def cosine_similarity(vec1, vec2):
    """
    コサイン類似度を計算
    """
    try:
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    except Exception as e:
        logger.error(f"コサイン類似度計算中にエラー: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def clean_html(raw_html: str) -> str:
    """
    HTMLタグを除去してテキストのみを返す
    """
    try:
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        logger.error(f"HTML処理中にエラー: {str(e)}")
        logger.error(traceback.format_exc())
        return raw_html  # エラー時は元のテキストを返す

def search_faq(user_message: str, user_info: dict, reply_token: str) -> str:
    """
    FAQデータを検索し、ユーザーの履歴を考慮して回答を生成
    """
    start_time = time.time()
    try:
        # 環境情報をログに記録
        env_info = "AWS環境" if is_aws_environment() else "ローカル環境"
        logger.info(f"search_faq関数が呼び出されました: user_message={user_message}, reply_token={reply_token}, 環境={env_info}")
        user_id = user_info.get('id')

        if not user_id:
            logger.warning("ユーザーIDが見つかりません")
            message = "会員登録がまだ完了していないようです。ぜひ会員登録をして、すべての機能をご利用ください！"
            send_reply_with_retry(reply_token, message)
            return message

        user_nickname = user_info.get('nickname', 'ユーザー')
        user_sex = user_info.get('sex', 'NULL')
        logger.debug(f"ユーザー{user_id}の情報: nickname={user_nickname}, sex={user_sex}")

        # リセットの場合、履歴を削除し、削除後の履歴をログに出力
        if user_message.upper() == "リセット":
            if user_id in USER_CONVERSATIONS:
                USER_CONVERSATIONS[user_id].clear()  # キーを保持しつつ内容をクリア
                del USER_CONVERSATIONS[user_id]  # キーごと完全削除

            logger.info(f"{user_id} の履歴を削除しました")
            message = "ありがとうございました。またお気軽に質問してくださいね"
            send_reply_with_retry(reply_token, message)
            return message

        # 履歴をログに出力
        logger.debug(f"{user_id} の現在の履歴: {USER_CONVERSATIONS.get(user_id, '履歴なし')}")

        # 履歴を保存
        if user_id not in USER_CONVERSATIONS:
            USER_CONVERSATIONS[user_id] = []

        # 5往復（10発言）以上なら古いものから削除
        while len(USER_CONVERSATIONS[user_id]) >= 10:
            USER_CONVERSATIONS[user_id].pop(0)

        USER_CONVERSATIONS[user_id].append({"user": user_message})

        # microcms_faq_embeddings.json からFAQデータを読み込む
        try:
            # ファイルの存在確認
            if not os.path.exists(FAQ_DATA_PATH):
                logger.error(f"FAQデータファイルが見つかりません: {FAQ_DATA_PATH}")
                message = "システムエラーが発生しました。しばらくしてから再度お試しください。"
                send_reply_with_retry(reply_token, message)
                return message
                
            with open(FAQ_DATA_PATH, 'r') as f:
                faqs = json.load(f)
            logger.debug(f"FAQデータを正常に読み込みました: {len(faqs)}件")
        except Exception as e:
            logger.error(f"FAQデータの読み込み中にエラー: {str(e)}")
            logger.error(traceback.format_exc())
            message = "システムエラーが発生しました。しばらくしてから再度お試しください。"
            send_reply_with_retry(reply_token, message)
            return message

        # 性別でFAQをフィルタリング
        matched_faqs = [
            faq for faq in faqs 
            if faq['sex'] == user_sex or faq['sex'] == 'NULL'
        ]
        logger.debug(f"性別{user_sex}にマッチしたFAQ: {len(matched_faqs)}件")

        # ユーザーの質問に最も近いFAQを 複数 取得
        try:
            user_embedding = get_embedding(user_message)
            logger.debug("ユーザーメッセージのEmbeddingを取得しました")
        except Exception as e:
            logger.error(f"ユーザーメッセージのEmbedding取得中にエラー: {str(e)}")
            logger.error(traceback.format_exc())
            message = "システムエラーが発生しました。しばらくしてから再度お試しください。"
            send_reply_with_retry(reply_token, message)
            return message
            
        relevant_faqs = []
        try:
            for faq in matched_faqs:
                faq_embedding = faq['embedding']
                similarity = cosine_similarity(user_embedding, faq_embedding)
                if similarity > 0.85:  # 類似度が0.85以上のものを収集
                    relevant_faqs.append((faq, similarity))

            # 類似度の高い順にソート
            relevant_faqs.sort(key=lambda x: x[1], reverse=True)
            logger.debug(f"関連するFAQが{len(relevant_faqs)}件見つかりました")
        except Exception as e:
            logger.error(f"FAQ類似度計算中にエラー: {str(e)}")
            logger.error(traceback.format_exc())
            message = "システムエラーが発生しました。しばらくしてから再度お試しください。"
            send_reply_with_retry(reply_token, message)
            return message

        # 過去の会話履歴を取得
        conversation_history = "\n".join(
            [f"ユーザー: {conv['user']}" if 'user' in conv else f"ボット: {conv['bot']}" 
            for conv in USER_CONVERSATIONS[user_id][-10:]]
        ) if USER_CONVERSATIONS[user_id] else "履歴なし"

        # FAQが1つ以上見つかった場合
        if relevant_faqs:
            try:
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
                logger.debug("FAQから回答を生成します")
            except Exception as e:
                logger.error(f"FAQ回答準備中にエラー: {str(e)}")
                logger.error(traceback.format_exc())
                message = "システムエラーが発生しました。しばらくしてから再度お試しください。"
                send_reply_with_retry(reply_token, message)
                return message

        # FAQで見つからなかった場合
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
            logger.debug("一般的な回答を生成します")

        # OpenAIから回答を取得
        try:
            reply = get_openai_reply(user_message, system_prompt)
            logger.debug(f"OpenAIから回答を取得しました: {reply[:50]}...")
        except Exception as e:
            logger.error(f"OpenAIからの回答取得中にエラー: {str(e)}")
            logger.error(traceback.format_exc())
            message = "現在、サービスが込み合っています。しばらくしてから再度お試しください。"
            send_reply_with_retry(reply_token, message)
            return message

        # 履歴に Bot の回答も追加
        USER_CONVERSATIONS[user_id].append({"bot": reply})

        # LINEへメッセージ送信
        send_result = send_reply_with_retry(reply_token, reply)
        
        if not send_result:
            logger.error("3回の再試行後もLINEへの送信が失敗しました")
            return "LINEへの送信が失敗しました。"
        
        logger.info(f"FAQ検索処理完了: 処理時間={time.time() - start_time:.2f}秒")
        return reply

    except Exception as e:
        logger.error(f"FAQ検索中に予期せぬエラー: {str(e)}")
        logger.error(traceback.format_exc())
        try:
            message = "システムエラーが発生しました。しばらくしてから再度お試しください。"
            send_reply_with_retry(reply_token, message)
        except Exception as inner_e:
            logger.error(f"エラー通知送信中にさらにエラー: {str(inner_e)}")
            logger.error(traceback.format_exc())
        return "FAQ検索中にエラーが発生しました。"

# LINEへの送信を再試行する関数
def send_reply_with_retry(reply_token, message, max_retries=3, retry_delay=1):
    """
    LINEへの送信を最大3回再試行する
    """
    for attempt in range(max_retries):
        try:
            # 長すぎるメッセージを分割
            if len(message) > 4500:  # LINE APIの制限は5000文字だが余裕を持たせる
                logger.warning(f"メッセージが長すぎるため分割します: {len(message)}文字")
                message = message[:4500] + "\n\n(メッセージが長すぎるため省略されました)"
            
            result = send_line_reply(reply_token, message)
            if result:
                logger.info(f"LINEへの送信が成功: {attempt+1}回目")
                return True
            else:
                logger.warning(f"LINEへの送信が失敗: {attempt+1}回目")
                if attempt < max_retries - 1:
                    logger.info(f"{retry_delay}秒後に再試行します")
                    time.sleep(retry_delay)
                    # 再試行の間隔を少し長くする
                    retry_delay *= 2
        except Exception as e:
            logger.error(f"LINEへの送信中に例外: {attempt+1}回目 - {str(e)}")
            logger.error(traceback.format_exc())
            if attempt < max_retries - 1:
                logger.info(f"{retry_delay}秒後に再試行します")
                time.sleep(retry_delay)
                # 再試行の間隔を少し長くする
                retry_delay *= 2
    
    return False
