from datetime import datetime
import pytz
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.models.user import User
from typing import Optional, List, Dict, Any

class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        ユーザーIDでユーザーを取得
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        メールアドレスでユーザーを取得
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_line_id(self, line_id: str) -> Optional[User]:
        """
        LINE IDでユーザーを取得
        """
        return self.db.query(User).filter(User.line_id == line_id).first()

    def get_user_by_invitation_id(self, invitation_id: str) -> Optional[User]:
        """
        invitation_idでユーザーを取得
        """
        return self.db.query(User).filter(User.invitation_id == invitation_id).first()

    def get_users_without_invitation_id(self) -> List[User]:
        """
        invitation_idが未設定のユーザーを取得
        """
        return self.db.query(User).filter(
            (User.invitation_id == None) | (User.invitation_id == "")
        ).all()

    def create_user(self, **kwargs) -> User:
        """
        新しいユーザーを作成
        """
        try:
            new_user = User(**kwargs)
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """
        ユーザー情報を更新
        
        Args:
            user_id: 更新するユーザーのID
            update_data: 更新するフィールドと値の辞書
            
        Returns:
            更新されたユーザーオブジェクト、ユーザーが存在しない場合はNone
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        try:
            for key, value in update_data.items():
                setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

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

    def delete_user(self, user_id: int) -> bool:
        """
        ユーザーを削除
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        try:
            self.db.delete(user)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
