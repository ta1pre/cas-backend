from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.features.media.services.media_service import get_presigned_url, save_uploaded_file_info
from app.features.media.schemas.media_schema import MediaUploadRequest, GetMediaRequest, RegisterMediaRequest, MediaDeleteRequest
from app.db.models.media_files import MediaFile
from app.features.media.services.media_delete import delete_s3_file
from app.features.media.repositories.media_repository import delete_media_records


router = APIRouter()

# ✅ 署名付きURLの発行エンドポイント
@router.post("/generate-url")
def create_presigned_url(
    request: MediaUploadRequest,
    current_user: int = Depends(get_current_user)
):
    try:
        print(f"[INFO] 🔐 ユーザー認証成功: user_id={current_user}")  # ✅ 認証が成功しているか確認

        presigned_url = get_presigned_url(
            request.file_name,
            request.file_type,
            request.target_type,
            request.target_id,
            request.order_index
        )
        print(f"[DEBUG] 生成された presigned_url: {presigned_url}")
        return {"presigned_url": presigned_url}
    except Exception as e:
        print(f"[ERROR] S3 URLの生成に失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"S3 URLの生成に失敗しました: {str(e)}")

@router.post("/get-by-index")
def get_media_by_index(
    request: GetMediaRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    `target_type`, `target_id`, `order_index` に紐づく画像情報を取得
    """
    media_files = db.query(MediaFile).filter(
        MediaFile.target_type == request.target_type,
        MediaFile.target_id == request.target_id,
        MediaFile.order_index == request.order_index
    ).all()

    if not media_files:
        return []  # 該当データなしの場合は空のリスト

    return [
        {
            "media_id": media.id,
            "file_url": media.file_url,
            "file_type": media.file_type,
            "target_type": media.target_type,
            "target_id": media.target_id,
            "order_index": media.order_index
        }
        for media in media_files
    ]
#画像情報をDB登録
@router.post("/register")
def register_media(
    request: RegisterMediaRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    アップロードされた画像情報をDBに登録する
    """
    try:
        # ✅ 新しい画像をDBに登録
        new_media = MediaFile(
            file_url=request.file_url,
            file_type=request.file_type,
            target_type=request.target_type,
            target_id=request.target_id,
            order_index=request.order_index
        )
        db.add(new_media)
        db.commit()
        db.refresh(new_media)

        print(f"[INFO] ✅ 新しいメディア登録成功: {new_media.file_url}, ID: {new_media.id}")
        return {"status": "success", "file_url": new_media.file_url, "id": new_media.id}

    except Exception as e:
        db.rollback()
        print(f"[ERROR] DB登録エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="DB登録に失敗しました")

#削除   
@router.post("/delete")
def delete_media(
    request: MediaDeleteRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    `target_type`, `target_id`, `order_index` に紐づくメディアを削除
    """
    print(f"[INFO] 🔥 /delete リクエスト受信: {request.model_dump()}")

    # ✅ 1. DB からメディア情報を取得
    media_files = db.query(MediaFile).filter(
        MediaFile.target_type == request.target_type,
        MediaFile.target_id == request.target_id,
        MediaFile.order_index == request.order_index
    ).all()

    if not media_files:
        print("[INFO] ℹ️ 削除対象のメディアなし")
        return {"status": "success", "message": "削除対象なし"}

    # ✅ 2. S3 から削除
    for media in media_files:
        print(f"[INFO] 🗑️ S3 から削除するファイル: {media.file_url}")
        if not delete_s3_file(media.file_url):
            raise HTTPException(status_code=500, detail="S3 の削除に失敗しました")

    # ✅ 3. DB から削除
    print("[INFO] 🗑️ DB から削除を開始")
    if not delete_media_records(db, request.target_type, request.target_id, request.order_index):
        raise HTTPException(status_code=500, detail="DB の削除に失敗しました")

    print("[INFO] ✅ 画像削除成功")
    return {"status": "success", "message": "S3とDBのメディアが削除されました。"}

# メディアのターゲット情報を更新するエンドポイント
class UpdateMediaTargetRequest(BaseModel):
    media_id: int = Field(..., description="メディアID")
    target_type: str = Field(..., description="ターゲットタイプ（例：post, profile）")
    target_id: int = Field(..., description="ターゲットID（例：投稿ID）")

@router.post("/update-target")
def update_media_target(
    request: UpdateMediaTargetRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    メディアのターゲット情報（target_typeとtarget_id）を更新する
    主に、仮IDでアップロードした画像を実際の投稿IDに紐付ける際に使用
    """
    try:
        # メディアIDから該当レコードを検索
        media = db.query(MediaFile).filter(MediaFile.id == request.media_id).first()
        
        if not media:
            raise HTTPException(status_code=404, detail=f"メディアID {request.media_id} が見つかりません")
        
        # ターゲット情報を更新
        media.target_type = request.target_type
        media.target_id = request.target_id
        
        db.commit()
        db.refresh(media)
        
        print(f"[INFO] ✅ メディア(ID: {media.id})のターゲット情報を更新: {media.target_type}/{media.target_id}")
        return {
            "status": "success", 
            "message": "メディアのターゲット情報を更新しました",
            "media": {
                "id": media.id,
                "file_url": media.file_url,
                "target_type": media.target_type,
                "target_id": media.target_id
            }
        }
        
    except HTTPException as he:
        # HTTPExceptionはそのまま再送
        raise he
    except Exception as e:
        db.rollback()
        print(f"[ERROR] メディアのターゲット情報更新エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"メディアのターゲット情報更新に失敗しました: {str(e)}")
