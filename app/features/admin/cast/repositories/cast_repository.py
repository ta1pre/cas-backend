"""Repository for admin cast operations"""
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
import boto3
from urllib.parse import urlparse

from app.db.models.user import User
from app.db.models.cast_identity_verification import CastIdentityVerification
from app.db.models.media_files import MediaFile

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
        
        # 各キャストの画像情報を取得
        items = []
        for record in records:
            cast_data = {
                "id": record.id,
                "nick_name": record.nick_name,
                "status": record.status,
                "thumbnail_url": None,
                "document_count": 0
            }
            
            # 身分証画像情報を取得
            media_files = (
                self.db.query(MediaFile)
                .filter(
                    MediaFile.target_type == "cast_identity_verification",
                    MediaFile.target_id == record.id,
                )
                .order_by(MediaFile.created_at.desc())
                .all()
            )
            
            if media_files:
                cast_data["document_count"] = len(media_files)
                # 最新の画像をサムネイルとして使用
                cast_data["thumbnail_url"] = self._generate_presigned_url(media_files[0].file_url)
            
            items.append(cast_data)
        
        return total, items

    def _generate_presigned_url(self, original_url: str) -> str:
        """S3 presigned URLを生成"""
        try:
            s3_client = boto3.client(
                "s3",
                region_name=os.getenv("AWS_REGION", "ap-northeast-1"),
            )
            bucket_name = os.getenv("S3_BUCKET_NAME", "cast-media")
            
            # 既に ?Expires= が付与されていればキーを抽出
            if original_url.startswith("https://"):
                parsed = urlparse(original_url)
                key = parsed.path.lstrip("/")
            else:
                key = original_url.lstrip("/")
                
            return s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key},
                ExpiresIn=60 * 60,  # 1時間
            )
        except Exception as e:
            print(f"[cast_repository] presign error: {e}")
            # フォールバックとして元URLを返す
            return original_url
