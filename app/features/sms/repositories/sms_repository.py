import os
import boto3
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.user import User  # ✅ ORMモデルのインポート
from sqlalchemy import and_
from datetime import datetime
import pytz


class SMSRepository:
    def __init__(self, db: Session):
        self.db = db

        # ✅ AWS認証情報の取得
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_REGION", "ap-northeast-1")

        # ✅ SNSクライアントのセッション管理
        session = boto3.session.Session()
        self.sns_client = session.client(
            "sns",
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def send_sms(self, phone_number: str, message: str):
        """
        ✅ AWS SNSを使ってSMSを送信
        """
        try:
            response = self.sns_client.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            print(f"✅ SMS送信成功: MessageId: {response.get('MessageId')}")
            return True
        except Exception as e:
            print(f"❌ SMS送信失敗: {e}")
            return False

    def save_verification_code(self, user_id: int, phone: str, code: str):
        """
        ✅ 認証コードを保存し、SNSでSMS送信
        """
        try:
            # 1️⃣ ORMでユーザー情報を取得
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user:
                print(f"❌ User ID {user_id} not found.")
                return False

            print(f"✅ 更新前: mobile_phone={user.mobile_phone}, code={user.phone_verification_code}")

            # ✅ JSTの現在時刻を取得
            jst = pytz.timezone('Asia/Tokyo')
            now_jst = datetime.now(jst)

            # 2️⃣ 認証コード・電話番号・updated_at を更新
            user.mobile_phone = phone
            user.phone_verification_code = code
            user.updated_at = now_jst  # ✅ 明示的に更新

            # 3️⃣ ORMで変更を確実に反映
            self.db.add(user)      # ✅ 明示的に追加
            self.db.commit()       # ✅ コミットで確定
            self.db.refresh(user)  # ✅ オブジェクトの最新化

            print(f"✅ 更新後: mobile_phone={user.mobile_phone}, code={user.phone_verification_code}, updated_at={user.updated_at}")

            # 4️⃣ SMS送信
            message = f"[認証コード] {code}（5分以内に入力してください）"
            return self.send_sms(phone, message)

        except Exception as e:
            self.db.rollback()
            print(f"❌ 認証コードの保存エラー: {e}")
            return False
        
    def verify_code(self, user_id: int, code: str) -> bool:
        """
        ✅ 認証コードを検証し、成功したらphone_verifiedを1に更新
        """
        user = self.db.query(User).filter(
            User.id == user_id,
            User.phone_verification_code == code
        ).first()

        if not user:
            print("❌ 認証コードが一致しません")
            return False

        try:
            user.phone_verified = 1  # ✅ 認証済みに更新
            user.phone_verification_code = None  # ✅ 認証コードの削除

            # ✅ 変更を確実に反映
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            print("✅ 電話番号認証が完了しました")
            return True
        except Exception as e:
            self.db.rollback()
            print(f"❌ 認証処理エラー: {e}")
            return False
