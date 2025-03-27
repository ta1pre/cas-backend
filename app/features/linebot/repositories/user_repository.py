from sqlalchemy.orm import Session
from app.db.models.user import User
from typing import Optional
from datetime import datetime
import pytz
from sqlalchemy.exc import SQLAlchemyError



class LinebotUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_line_id(self, line_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.line_id == line_id).first()

    def update_last_login(self, line_id: str) -> Optional[User]:
        """
        ✅ LINE IDを使用して最終ログイン日時を更新（日本時間）
        """
        user = self.get_user_by_line_id(line_id)
        if not user:
            return None
        try:
            # ✅ JSTの現在時刻を取得
            jst = pytz.timezone('Asia/Tokyo')
            now_jst = datetime.now(jst)

            # ✅ last_login を JSTで更新
            user.last_login = now_jst.strftime("%Y/%m/%d %H:%M:%S")

            self.db.commit()
            self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e