from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.cast_identity_verification import CastIdentityVerification
from app.db.models.media_files import MediaFile
from fastapi import HTTPException
from typing import List, Optional

class IdentityVerificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_verification_status(self, cast_id: int) -> Optional[CastIdentityVerification]:
        """
        本人確認申請を取得
        """
        # cast_idがUserオブジェクトの場合、id属性を取得
        if hasattr(cast_id, 'id'):
            cast_id = cast_id.id
            
        return self.db.query(CastIdentityVerification).filter(
            CastIdentityVerification.cast_id == cast_id
        ).first()

    def create_verification_request(self, cast_id: int, service_type: str, id_photo_media_id: int, juminhyo_media_id: Optional[int] = None,
                                   document_type: Optional[str] = None) -> CastIdentityVerification:
        """
        本人確認申請を取得
        """
        # cast_id が User オブジェクトの場合は id を取り出して数値化
        if hasattr(cast_id, "id"):
            cast_id = cast_id.id
        
        print(f"メッセージ: create_verification_request呼び出し - cast_id={cast_id}, service_type={service_type}, id_photo_media_id={id_photo_media_id}, juminhyo_media_id={juminhyo_media_id}, document_type={document_type}")
        
        # 既存の本人確認申請を取得
        existing = self.get_verification_status(cast_id)
        print(f"既存の本人確認申請結果: {existing}")
        
        if existing:
            # 既に承認済みの場合、エラー
            if existing.status == 'approved':
                print(f"エラー: 既に承認済み")
                raise HTTPException(status_code=400, detail="既に承認済みです")
            
            # 審査中の場合、エラー
            if existing.status == 'pending':
                print(f"エラー: 審査中")
                raise HTTPException(status_code=400, detail="審査中です。しばらくお待ちください")
            
            # 審査結果を更新
            print(f"既存の本人確認申請を更新: status={existing.status} -> pending")
            existing.status = 'pending'
            existing.submitted_at = func.now()
            existing.reviewed_at = None
            existing.rejection_reason = None
            existing.service_type = service_type
            existing.id_photo_media_id = id_photo_media_id
            existing.juminhyo_media_id = juminhyo_media_id
            existing.document_type = document_type
            
            try:
                self.db.commit()
                print(f"更新成功: {existing}")
                return existing
            except Exception as e:
                self.db.rollback()
                print(f"更新失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"データベース更新エラー: {str(e)}")
        
        # 新規本人確認申請を作成
        print("新規本人確認申請を作成")
        try:
            new_verification = CastIdentityVerification(
                cast_id=cast_id,
                status='pending',
                submitted_at=func.now(),
                service_type=service_type,
                id_photo_media_id=id_photo_media_id,
                juminhyo_media_id=juminhyo_media_id,
                document_type=document_type
            )
            self.db.add(new_verification)
            self.db.commit()
            self.db.refresh(new_verification)
            print(f"新規本人確認申請成功: {new_verification}")
            return new_verification
        except Exception as e:
            self.db.rollback()
            print(f"新規本人確認申請失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=f"データベース更新エラー: {str(e)}")

    def update_verification_status(self, cast_id: int, status: str, reviewer_id: int, rejection_reason: Optional[str] = None) -> CastIdentityVerification:
        """
        本人確認申請を更新します。管理者用
        """
        verification = self.get_verification_status(cast_id)
        if not verification:
            raise HTTPException(status_code=404, detail="本人確認申請が見つかりません")
        
        verification.status = status
        verification.reviewed_at = func.now()
        verification.reviewer_id = reviewer_id
        
        if status == 'rejected' and rejection_reason:
            verification.rejection_reason = rejection_reason
        
        self.db.commit()
        self.db.refresh(verification)
        return verification

    def get_verification_documents(self, cast_id: int) -> List[MediaFile]:
        """
        本人確認申請のドキュメントを取得します
        """
        return self.db.query(MediaFile).filter(
            MediaFile.target_type == 'identity_verification',
            MediaFile.target_id == cast_id
        ).all()

    def upload_basic_document(self, cast_id: int, id_photo_media_id: int, document_type: str) -> CastIdentityVerification:
        """
        基本身分証をアップロードします
        """
        # cast_id が User オブジェクトの場合は id を取り出して数値化
        if hasattr(cast_id, "id"):
            cast_id = cast_id.id
        
        # 既存の本人確認申請を取得
        verification = self.get_verification_status(cast_id)
        
        if not verification:
            # 本人確認申請が見つからない場合、新規作成
            verification = CastIdentityVerification(
                cast_id=cast_id,
                status='unsubmitted',
                service_type='A',
                id_photo_media_id=id_photo_media_id,
                document_type=document_type
            )
            self.db.add(verification)
        else:
            # 既存の本人確認申請を更新
            verification.id_photo_media_id = id_photo_media_id
            verification.document_type = document_type
        
        try:
            self.db.commit()
            self.db.refresh(verification)
            return verification
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"データベース更新エラー: {str(e)}")

    def upload_residence_document(self, cast_id: int, juminhyo_media_id: int) -> CastIdentityVerification:
        """
        住民票をアップロードします
        """
        # cast_id が User オブジェクトの場合は id を取り出して数値化
        if hasattr(cast_id, "id"):
            cast_id = cast_id.id
        
        # 既存の本人確認申請を取得
        verification = self.get_verification_status(cast_id)
        
        if not verification:
            # 本人確認申請が見つからない場合、エラー
            raise HTTPException(status_code=400, detail="基本身分証を先にアップロードしてください")
        
        # 住民票を更新
        verification.juminhyo_media_id = juminhyo_media_id
        
        # 両方の書類が揃ったらステータスをpendingに
        if verification.id_photo_media_id and verification.juminhyo_media_id:
            verification.status = 'pending'
            verification.submitted_at = func.now()
        
        try:
            self.db.commit()
            self.db.refresh(verification)
            return verification
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"データベース更新エラー: {str(e)}")
