import uuid
import string
import random
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.features.account.repositories.account_repository import AccountRepository
from typing import Optional, Dict, Any, List
from app.db.models.user import User

class AccountService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)
    
    def get_user_by_line_id(self, line_id: str) -> Optional[User]:
        """
        LINE IDでユーザーを取得
        """
        return self.account_repo.get_user_by_line_id(line_id)
    
    def update_last_login(self, line_id: str) -> Optional[User]:
        """
        最終ログイン日時を更新
        """
        return self.account_repo.update_last_login(line_id)
    
    def create_user(self, **user_data) -> User:
        """
        ユーザーを作成し、invitation_idが設定されていない場合のみ一意のIDを生成
        
        Args:
            **user_data: ユーザー作成に必要なデータ
            
        Returns:
            作成されたユーザーオブジェクト
        """
        # 既存のユーザーデータをコピーして変更を加える（元のデータを変更しない）
        user_data_copy = user_data.copy()
        
        # invitation_idが未設定または空の場合のみ生成
        if 'invitation_id' not in user_data_copy or not user_data_copy['invitation_id']:
            user_data_copy['invitation_id'] = self._generate_unique_invitation_id()
        
        # リポジトリを使用してユーザーを作成
        return self.account_repo.create_user(**user_data_copy)
    
    def ensure_user_has_invitation_id(self, user_id: int) -> Optional[User]:
        """
        既存ユーザーのinvitation_idが未設定の場合に設定する
        
        Args:
            user_id: ユーザーID
            
        Returns:
            更新されたユーザーオブジェクト
        """
        user = self.account_repo.get_user_by_id(user_id)
        if user and not user.invitation_id:
            invitation_id = self._generate_unique_invitation_id()
            return self.account_repo.update_user(user_id, {"invitation_id": invitation_id})
        return user
    
    def batch_generate_invitation_ids(self) -> int:
        """
        invitation_idが未設定の全ユーザーに対して一意のIDを生成して設定
        
        Returns:
            更新されたユーザー数
        """
        users_without_invitation = self.account_repo.get_users_without_invitation_id()
        updated_count = 0
        
        for user in users_without_invitation:
            invitation_id = self._generate_unique_invitation_id()
            self.account_repo.update_user(user.id, {"invitation_id": invitation_id})
            updated_count += 1
        
        return updated_count
    
    def _generate_unique_invitation_id(self, length: int = 10) -> str:
        """
        一意のinvitation_idを生成します
        重複がある場合は再生成します
        
        Args:
            length: 生成するIDの長さ（デフォルト: 10）
            
        Returns:
            生成された一意のinvitation_id
            
        Raises:
            ValueError: 最大試行回数を超えても一意のIDが生成できない場合
        """
        max_attempts = 10  # 最大試行回数
        
        for _ in range(max_attempts):
            # ランダム文字列生成（英数字）
            chars = string.ascii_letters + string.digits
            invitation_id = ''.join(random.choice(chars) for _ in range(length))
            
            # 既存のinvitation_idと重複していないか確認
            existing_user = self.account_repo.get_user_by_invitation_id(invitation_id)
            if not existing_user:
                return invitation_id
        
        # 最大試行回数を超えた場合はエラー
        raise ValueError("一意のinvitation_idを生成できませんでした。後でもう一度お試しください。")
