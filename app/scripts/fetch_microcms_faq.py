import json
import requests
from openai import OpenAI
from app.core.config import OPENAI_API_KEY, MICROCMS_API_URL, MICROCMS_API_KEY

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
    headers = {
        "X-MICROCMS-API-KEY": MICROCMS_API_KEY
    }

    embedded_faqs = []
    limit = 1000  # 1回で取得する最大件数
    offset = 0   # 取得開始位置

    while True:
        url = f"{MICROCMS_API_URL}?limit={limit}&offset={offset}"
        print(f"📡 リクエストURL: {url}")

        response = requests.get(url, headers=headers)
        print(f"📊 ステータスコード: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ FAQデータの取得失敗: {response.status_code}, {response.text}")
            break

        try:
            data = response.json()
            faqs = data.get('contents', [])
            print(f"📊 取得件数: {len(faqs)} (offset: {offset})")

            if not faqs:
                print("✅ すべてのデータを取得しました。")
                break

            for faq in faqs:
                question = faq.get('title')
                answer = faq.get('content')
                category = faq.get('category', {}).get('id')  # category.idの取得
                article_id = faq.get('id')  # 🔹 MicroCMSのFAQ IDを取得（記事IDとして使う）

                if question and answer and category and article_id:
                    sex = CATEGORY_MAPPING.get(category, 'NULL')  # カテゴリから性別を判定
                    embedding = get_embedding(question)  # 質問文を埋め込み変換

                    embedded_faqs.append({
                        "question": question,
                        "answer": answer,
                        "sex": sex,
                        "category": category,
                        "article_id": article_id,  # 🔹 記事IDを保存
                        "embedding": embedding
                    })
                    print(f"✅ Embedding生成: {question} (カテゴリ: {category}, 性別: {sex}, 記事ID: {article_id})")
                else:
                    print(f"⚠️ 無効なFAQエントリ: {faq}")

            # 次のページへ
            offset += limit

        except Exception as e:
            print(f"❌ レスポンスの解析中にエラー: {e}")
            break

    # FAQデータを直接埋め込みJSONとして保存
    with open('app/data/microcms_faq_embeddings.json', 'w') as f:
        json.dump(embedded_faqs, f, indent=4, ensure_ascii=False)

    print("✅ FAQ Embeddingデータが正常に保存されました。")

if __name__ == "__main__":
    fetch_and_embed_faq()
