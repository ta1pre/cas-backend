import json
from openai import OpenAI
from app.core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str) -> list:
    """
    OpenAI APIでテキストをEmbeddingに変換する
    """
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def generate_faq_embeddings():
    """
    取得したFAQデータをEmbeddingに変換して保存
    """
    # 📌 修正: ファイル名を正しいものに変更
    with open('app/data/raw_microcms_faq.json', 'r') as f:
        faqs = json.load(f)

    embedded_faqs = []
    for faq in faqs:
        question = faq.get('question')
        answer = faq.get('answer')
        sex = faq.get('sex', 'NULL')
        category = faq.get('category', 'unknown')
        
        if question and answer:
            embedding = get_embedding(question)
            embedded_faqs.append({
                "question": question,
                "answer": answer,
                "sex": sex,
                "category": category,
                "embedding": embedding
            })
            print(f"✅ Embedding生成: {question} (性別: {sex}, カテゴリ: {category})")

    # 保存先も確認
    with open('app/data/microcms_faq_embeddings.json', 'w') as f:
        json.dump(embedded_faqs, f, indent=4, ensure_ascii=False)

    print("✅ FAQ Embeddingデータが正常に保存されました。")

if __name__ == "__main__":
    generate_faq_embeddings()
