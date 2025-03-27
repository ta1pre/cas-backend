import boto3
import os
from dotenv import load_dotenv

# ✅ 環境変数の読み込み
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_S3_REGION = os.getenv("AWS_S3_REGION")

# ✅ S3クライアントの初期化
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION
)

# ✅ S3 署名付きURLの発行
# ✅ S3 署名付きURLの発行
def generate_presigned_url(file_name: str, file_type: str, target_type: str, target_id: int, order_index: int):
    """
    S3 にアップロードするための署名付きURLを発行
    """
    key = f"{target_id}/{target_type}/{order_index}/{file_name}"  # ✅ ディレクトリ構造を変更

    return s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": AWS_S3_BUCKET_NAME, "Key": key, "ContentType": file_type},
        ExpiresIn=3600  # ✅ 1時間の有効期限
    )

