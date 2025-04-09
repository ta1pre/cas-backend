import json
import requests
from openai import OpenAI
from app.core.config import OPENAI_API_KEY, MICROCMS_API_URL, MICROCMS_API_KEY
import logging
import os
import time
import traceback

# ロガーの設定
logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

# カテゴリと性別のマッピング
CATEGORY_MAPPING = {
    "common": "NULL",
    "common_q": "NULL",
    "guest": "male",
    "guest_q": "male",
    "cast": "female",
    "cast_q": "female"
}

def get_embedding(text: str) -> list:
    """
    OpenAI APIでテキストをEmbeddingに変換する
    """
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def fetch_and_embed_faq():
    """
    MicroCMSからFAQデータを取得し、埋め込みを生成して保存
    """
    start_time = time.time()
    logger.info(f"FAQ更新処理を開始しました: {start_time}")
    
    headers = {
        "X-MICROCMS-API-KEY": MICROCMS_API_KEY
    }

    embedded_faqs = []
    limit = 100  # 1回で取得する最大件数（MicroCMS APIの制限は100）
    offset = 0   # 取得開始位置

    try:
        # カレントディレクトリを出力
        current_dir = os.getcwd()
        logger.info(f"カレントディレクトリ: {current_dir}")
        
        # APIキーの確認
        if not MICROCMS_API_KEY:
            logger.error("MICROCMS_API_KEYが設定されていません")
            return False
        
        if not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEYが設定されていません")
            return False
            
        while True:
            url = f"{MICROCMS_API_URL}?limit={limit}&offset={offset}"
            logger.info(f"MicroCMS APIリクエスト: {url}")

            try:
                response = requests.get(url, headers=headers)
                logger.info(f"MicroCMS APIレスポンス: ステータスコード={response.status_code}")

                if response.status_code != 200:
                    logger.error(f"MicroCMS APIエラー: {response.status_code}, {response.text}")
                    return False

                data = response.json()
                faqs = data.get('contents', [])
                logger.info(f"取得したFAQ件数: {len(faqs)} (offset: {offset})")

                if not faqs:
                    logger.info("すべてのデータを取得しました")
                    break

                for faq in faqs:
                    question = faq.get('title')
                    answer = faq.get('content')
                    category = faq.get('category', {}).get('id')
                    article_id = faq.get('id')

                    if question and answer and category and article_id:
                        sex = CATEGORY_MAPPING.get(category, 'NULL')
                        
                        try:
                            embedding = get_embedding(question)
                            embedded_faqs.append({
                                "question": question,
                                "answer": answer,
                                "sex": sex,
                                "category": category,
                                "article_id": article_id,
                                "embedding": embedding
                            })
                            logger.info(f"Embedding生成成功: {question[:30]}...")
                        except Exception as e:
                            logger.error(f"Embedding生成エラー: {str(e)}, 質問={question[:30]}...")
                            logger.error(traceback.format_exc())
                    else:
                        logger.warning(f"無効なFAQエントリ: {faq}")

                # 次のページへ
                offset += limit

            except Exception as e:
                logger.error(f"MicroCMS APIリクエスト中にエラー: {str(e)}")
                logger.error(traceback.format_exc())
                return False

        # ファイルを保存
        # 環境によらず動作するようにプロジェクトルートからの相対パスを構築
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, 'app', 'data', 'microcms_faq_embeddings.json')
        logger.info(f"FAQデータを保存します: {file_path}, 件数={len(embedded_faqs)}")
        
        try:
            # ディレクトリが存在するか確認し、存在しない場合は作成する
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                logger.info(f"ディレクトリが存在しないため作成します: {directory}")
                os.makedirs(directory, exist_ok=True)
                
            with open(file_path, 'w') as f:
                json.dump(embedded_faqs, f, indent=4, ensure_ascii=False)
            logger.info(f"FAQデータの保存に成功しました")
        except Exception as e:
            logger.error(f"FAQデータの保存中にエラー: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
        logger.info(f"FAQ更新処理が完了しました: 処理時間={time.time() - start_time:.2f}秒, 件数={len(embedded_faqs)}")
        return True
        
    except Exception as e:
        logger.error(f"FAQ更新処理中に予期せぬエラーが発生しました: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    fetch_and_embed_faq()
