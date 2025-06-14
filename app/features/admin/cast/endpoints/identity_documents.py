"""Admin Cast: 身分証画像取得エンドポイント"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import os
from urllib.parse import urlparse
import boto3

from app.db.session import get_db
from app.db.models.media_files import MediaFile
from app.features.admin.cast.schemas.identity_document import IdentityDocOut
from app.core.security import get_current_user  # ✅ 要: 管理者ユーザー認証

router = APIRouter()


@router.get("/{cast_id}/identity-documents", response_model=List[IdentityDocOut])
async def list_identity_documents(
    cast_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """指定キャストの身分証画像を取得

    - target_type は `cast_identity_verification` 固定
    - アップロード日時の降順で返す
    """
    records: List[MediaFile] = (
        db.query(MediaFile)
        .filter(
            MediaFile.target_type == "cast_identity_verification",
            MediaFile.target_id == cast_id,
        )
        .order_by(MediaFile.created_at.desc())
        .all()
    )

    if records is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found",
        )

        # S3 presigned URL を生成して返却
    s3_client = boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION", "ap-northeast-1"),
    )
    bucket_name = os.getenv("S3_BUCKET_NAME", "cast-media")

    def _make_url(original_url: str):
        # 既に ?Expires= が付与されていればキーを抽出
        if original_url.startswith("https://"):
            parsed = urlparse(original_url)
            key = parsed.path.lstrip("/")
        else:
            key = original_url.lstrip("/")
        try:
            return s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key},
                ExpiresIn=60 * 60,  # 1時間
            )
        except Exception as e:
            print("[identity_documents] presign error", e)
            # フォールバックとして元URLを返す
            return original_url

    return [
        IdentityDocOut(
            id=doc.id,
            url=_make_url(doc.file_url),
            created_at=doc.created_at,
            status=None,
        )
        for doc in records
    ]
