# app/features/customer/user_profile/service/user_profile_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.user import User
from app.features.customer.user_profile.schemas.user_profile_schema import UserProfileResponse, UpdateNicknameResponse

def get_user_profile(user_id: int, db: Session) -> UserProfileResponse:
    """u30e6u30fcu30b6u30fcu30d7u30edu30d5u30a3u30fcu30ebu60c5u5831u3092u53d6u5f97u3059u308b"""
    # u30e6u30fcu30b6u30fcu60c5u5831u3092u30c7u30fcu30bfu30d9u30fcu30b9u304bu3089u53d6u5f97
    user = db.query(User).filter(User.id == user_id).first()
    
    # u30e6u30fcu30b6u30fcu304cu5b58u5728u3057u306au3044u5834u5408u306fu30a8u30e9u30fc
    if not user:
        raise HTTPException(status_code=404, detail="u30e6u30fcu30b6u30fcu304cu898bu3064u304bu308au307eu305bu3093")
    
    # UserProfileResponseu30b9u30adu30fcu30deu306bu5909u63dbu3057u3066u8fd4u3059
    return UserProfileResponse.from_orm(user)

def update_user_nickname(user_id: int, nickname: str, db: Session) -> UpdateNicknameResponse:
    """u30cbu30c3u30afu30cdu30fcu30e0u3092u66f4u65b0u3059u308b"""
    # u30e6u30fcu30b6u30fcu60c5u5831u3092u30c7u30fcu30bfu30d9u30fcu30b9u304bu3089u53d6u5f97
    user = db.query(User).filter(User.id == user_id).first()
    
    # u30e6u30fcu30b6u30fcu304cu5b58u5728u3057u306au3044u5834u5408u306fu30a8u30e9u30fc
    if not user:
        raise HTTPException(status_code=404, detail="u30e6u30fcu30b6u30fcu304cu898bu3064u304bu308au307eu305bu3093")
    
    try:
        # u30cbu30c3u30afu30cdu30fcu30e0u3092u66f4u65b0
        user.nick_name = nickname
        db.commit()
        db.refresh(user)
        
        # u6210u529fu30ecu30b9u30ddu30f3u30b9u3092u8fd4u3059
        return UpdateNicknameResponse(
            message="u30cbu30c3u30afu30cdu30fcu30e0u3092u66f4u65b0u3057u307eu3057u305f",
            nick_name=nickname
        )
    except Exception as e:
        # u30a8u30e9u30fcu304cu767au751fu3057u305fu5834u5408u306fu30edu30fcu30ebu30d0u30c3u30af
        db.rollback()
        raise HTTPException(status_code=400, detail="u30cbu30c3u30afu30cdu30fcu30e0u306eu66f4u65b0u306bu5931u6557u3057u307eu3057u305f")
