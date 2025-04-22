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
        u672cu4ebau78bau8a8du7533u8acbu3092u4f5cu6210
        """
        return self.db.query(CastIdentityVerification).filter(
            CastIdentityVerification.cast_id == cast_id
        ).first()

    def create_verification_request(self, cast_id: int, service_type: str, id_photo_media_id: int, juminhyo_media_id: Optional[int] = None,
                                   bank_name: Optional[str] = None, branch_name: Optional[str] = None, 
                                   branch_code: Optional[str] = None, account_type: Optional[str] = None, 
                                   account_number: Optional[str] = None, account_holder: Optional[str] = None) -> CastIdentityVerification:
        """
        u672cu4ebau78bau8a8du7533u8acbu3092u4f5cu6210
        """
        print(f"u30eau30ddu30b8u30c8u30ea: create_verification_requestu958bu59cb - cast_id={cast_id}, service_type={service_type}, id_photo_media_id={id_photo_media_id}, juminhyo_media_id={juminhyo_media_id}")
        print(f"u53e3u5ea7u60c5u5831: bank_name={bank_name}, branch_name={branch_name}, branch_code={branch_code}, account_type={account_type}, account_number={account_number}, account_holder={account_holder}")
        
        # u65e2u5b58u306eu7533u8acbu304cu3042u308bu304bu78bau8a8d
        existing = self.get_verification_status(cast_id)
        print(f"u65e2u5b58u30ecu30b3u30fcu30c9u78bau8a8du7d50u679c: {existing}")
        
        if existing:
            # u65e2u306bu627fu8a8du6e08u307fu306eu5834u5408u306fu30a8u30e9u30fc
            if existing.status == 'approved':
                print(f"u30a8u30e9u30fc: u65e2u306bu627fu8a8du6e08u307f")
                raise HTTPException(status_code=400, detail="u65e2u306bu672cu4ebau78bau8a8du304cu5b8cu4e86u3057u3066u3044u307eu3059")
            
            # u5be9u67fbu4e2du306eu5834u5408u306fu30a8u30e9u30fc
            if existing.status == 'pending':
                print(f"u30a8u30e9u30fc: u5be9u67fbu4e2d")
                raise HTTPException(status_code=400, detail="u5be9u67fbu4e2du3067u3059u3002u3057u3070u3089u304fu304au5f85u3061u304fu3060u3055u3044")
            
            # u5374u4e0bu307eu305fu306fu672au63d0u51fau306eu5834u5408u306fu66f4u65b0
            print(f"u65e2u5b58u30ecu30b3u30fcu30c9u3092u66f4u65b0u3057u307eu3059: status={existing.status} -> pending")
            existing.status = 'pending'
            existing.submitted_at = func.now()
            existing.reviewed_at = None
            existing.rejection_reason = None
            existing.service_type = service_type
            existing.id_photo_media_id = id_photo_media_id
            existing.juminhyo_media_id = juminhyo_media_id
            
            # 口座情報を更新
            existing.bank_name = bank_name
            existing.branch_name = branch_name
            existing.branch_code = branch_code
            existing.account_type = account_type
            existing.account_number = account_number
            existing.account_holder = account_holder
            
            try:
                self.db.commit()
                print(f"u66f4u65b0u6210u529f: {existing}")
                return existing
            except Exception as e:
                self.db.rollback()
                print(f"u66f4u65b0u5931u6557: {str(e)}")
                raise HTTPException(status_code=500, detail=f"u30c7u30fcu30bfu30d9u30fcu30b9u66f4u65b0u30a8u30e9u30fc: {str(e)}")
        
        # u65b0u898fu4f5cu6210
        print("u65b0u898fu30ecu30b3u30fcu30c9u3092u4f5cu6210u3057u307eu3059")
        try:
            new_verification = CastIdentityVerification(
                cast_id=cast_id,
                status='pending',
                submitted_at=func.now(),
                service_type=service_type,
                id_photo_media_id=id_photo_media_id,
                juminhyo_media_id=juminhyo_media_id,
                # 口座情報を設定
                bank_name=bank_name,
                branch_name=branch_name,
                branch_code=branch_code,
                account_type=account_type,
                account_number=account_number,
                account_holder=account_holder
            )
            self.db.add(new_verification)
            self.db.commit()
            self.db.refresh(new_verification)
            print(f"u65b0u898fu4f5cu6210u6210u529f: {new_verification}")
            return new_verification
        except Exception as e:
            self.db.rollback()
            print(f"u65b0u898fu4f5cu6210u5931u6557: {str(e)}")
            raise HTTPException(status_code=500, detail=f"u30c7u30fcu30bfu30d9u30fcu30b9u4f5cu6210u30a8u30e9u30fc: {str(e)}")

    def update_verification_status(self, cast_id: int, status: str, reviewer_id: int, rejection_reason: Optional[str] = None) -> CastIdentityVerification:
        """
        u672cu4ebau78bau8a8du7533u8acbu3092u66f4u65b0u3059u3002u7d66u5e8fu7528
        """
        verification = self.get_verification_status(cast_id)
        if not verification:
            raise HTTPException(status_code=404, detail="u672cu4ebau78bau8a8du7533u8acbu304cu3067u3059")
        
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
        u672cu4ebau78bau8a8du7533u8acbu3092u4f5cu6210
        """
        return self.db.query(MediaFile).filter(
            MediaFile.target_type == 'identity_verification',
            MediaFile.target_id == cast_id
        ).all()

    def update_bank_account(self, cast_id: int, bank_name: str, branch_name: str, branch_code: str, 
                        account_type: str, account_number: str, account_holder: str) -> CastIdentityVerification:
        """
        u30abu30fcu30b9u30c8u306eu53e3u5ea7u60c5u5831u3092u66f4u65b0u3059u3002
        """
        # u65e2u5b58u30ecu30b3u30fcu30c9u3092u8fd4u3057u307eu3059
        verification = self.get_verification_status(cast_id)
        
        if not verification:
            # u30ecu30b3u30fcu30c9u304cu3067u3059u306au306fu65b0u898fu4f5cu6210
            verification = CastIdentityVerification(
                cast_id=cast_id,
                status='unsubmitted',  # u672cu4ebau78bau8a8du304cu5b8cu4e86u3057u3066u3044u307eu3059
                service_type='A',      # u30c7u30d5u30a2u30ebu30c8u30b9u306eu3067u3059
                bank_name=bank_name,
                branch_name=branch_name,
                branch_code=branch_code,
                account_type=account_type,
                account_number=account_number,
                account_holder=account_holder
            )
            self.db.add(verification)
        else:
            # u65e2u5b58u30ecu30b3u30fcu30c9u306eu53e3u5ea7u60c5u5831u3092u66f4u65b0
            verification.bank_name = bank_name
            verification.branch_name = branch_name
            verification.branch_code = branch_code
            verification.account_type = account_type
            verification.account_number = account_number
            verification.account_holder = account_holder
        
        try:
            self.db.commit()
            self.db.refresh(verification)
            return verification
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"u30c7u30fcu30bfu30d9u30fcu30b9u66f4u65b0u30a8u30e9u30fc: {str(e)}")
