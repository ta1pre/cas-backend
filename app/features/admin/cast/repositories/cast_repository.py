"""Repository for admin cast operations"""
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models.user import User
from app.db.models.cast_identity_verification import CastIdentityVerification

class CastRepository:
    """データベースからキャスト情報を取得するリポジトリ"""

    def update_identity_verification_status(
        self,
        cast_id: int,
        new_status: str,
        reviewer_id: int,
        rejection_reason: str | None = None,
    ) -> dict:
        """キャストの本人確認ステータスを更新 / 作成

        Returns updated record as dict.
        """
        record = (
            self.db.query(CastIdentityVerification)
            .filter(CastIdentityVerification.cast_id == cast_id)
            .one_or_none()
        )
        if record is None:
            record = CastIdentityVerification(cast_id=cast_id)
            self.db.add(record)

        record.status = new_status
        record.reviewer_id = reviewer_id
        record.reviewed_at = func.now()
        if new_status == "rejected":
            record.rejection_reason = rejection_reason or ""
        else:
            record.rejection_reason = None
        self.db.commit()
        self.db.refresh(record)
        return {
            "cast_id": record.cast_id,
            "status": record.status,
        }

    def __init__(self, db: Session):
        self.db = db

    def list_casts_with_status(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "id",
        sort_dir: str = "asc",
    ) -> Tuple[int, List[dict]]:
        """キャスト一覧と本人確認ステータスを取得

        Returns (total, items)
        """
        subquery = (
            self.db.query(
                CastIdentityVerification.cast_id.label("cast_id"),
                CastIdentityVerification.status.label("status"),
            )
            .subquery()
        )

        base_query = (
            self.db.query(
                User.id.label("id"),
                User.nick_name.label("nick_name"),
                func.coalesce(subquery.c.status, "unsubmitted").label("status"),
            )
            .outerjoin(subquery, subquery.c.cast_id == User.id)
            .filter(User.user_type == "cast")
        )

        # === ソート ===
        sort_columns = {
            "id": User.id,
            "nick_name": User.nick_name,
            "status": func.coalesce(subquery.c.status, "unsubmitted"),
        }
        order_col = sort_columns.get(sort_by, User.id)
        order_expr = order_col.asc() if sort_dir == "asc" else order_col.desc()
        print("### CastRepository ORDER", sort_by, sort_dir, order_expr)

        total = base_query.count()
        records = (
            base_query.order_by(order_expr)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        items = [
            {"id": r.id, "nick_name": r.nick_name, "status": r.status} for r in records
        ]
        return total, items
