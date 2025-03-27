import boto3
import os
from dotenv import load_dotenv

# ✅ 環境変数の読み込み
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_S3_REGION = os.getenv("AWS_S3_REGION")

# ✅ S3 クライアントの初期化
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION
)

def delete_s3_file(file_url: str) -> bool:
    """S3 から指定のファイルを削除"""
    try:
        file_key = file_url.split(f"https://{AWS_S3_BUCKET_NAME}.s3.amazonaws.com/")[-1]
        print(f"[INFO] 🗑️ S3 から削除対象のファイル: {file_key}")

        s3_client.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=file_key)
        print(f"[INFO] ✅ S3 ファイル削除成功: {file_key}")
        return True
    except Exception as e:
        print(f"[ERROR] ❌ S3 ファイル削除失敗: {str(e)}")
        return False
