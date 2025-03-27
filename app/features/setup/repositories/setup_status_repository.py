from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models.user import User
from app.db.models.cast_common_prof import CastCommonProf
from app.db.models.cast_rank import CastRank  # ✅ cast_rank のインポートを追加

class SetupStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    def update_user_profile(self, user_id: int, user_type: str, nickname: str = None):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.user_type = user_type
        user.sex = "female" if user_type == "cast" else "male"
        if user_type == "customer":
            user.nick_name = nickname

        self.db.commit()

    def get_default_rank_id(self):
        """ デフォルトの rank_id (1) が存在するか確認し、なければ作成 """
        rank = self.db.query(CastRank).filter(CastRank.id == 1).first()
        if not rank:
            new_rank = CastRank(id=1, rank_name="Default Rank", base_fee=0, description="デフォルトランク")
            self.db.add(new_rank)
            self.db.commit()
            return new_rank.id
        return rank.id

    def update_cast_profile(self, user_id: int, cast_name: str, age: int, height: int):
        cast_profile = self.db.query(CastCommonProf).filter(CastCommonProf.cast_id == user_id).first()
        if cast_profile:
            cast_profile.name = cast_name
            cast_profile.age = age
            cast_profile.height = height
        else:
            try:
                cast_profile = CastCommonProf(
                    cast_id=user_id,
                    cast_type='A',
                    rank_id=self.get_default_rank_id(),  # ✅ rank_id=1 を取得（存在することが保証されている）
                    name=cast_name,
                    age=age,
                    height=height
                )
                self.db.add(cast_profile)
                self.db.commit()
            except IntegrityError as e:
                self.db.rollback()
                raise HTTPException(status_code=400, detail=f"Invalid foreign key reference to cast_rank: {str(e)}")

#完了したかチェック
class SetupStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_setup_status(self, user_id: int) -> str:
        """ ユーザーの setup_status を取得 """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return "not_found"
        return user.setup_status or "incomplete"