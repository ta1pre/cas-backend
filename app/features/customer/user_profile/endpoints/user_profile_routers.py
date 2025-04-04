# app/features/customer/user_profile/endpoints/user_profile_routers.py

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# u8a8du8a3cu5fc5u9808u306eu30ebu30fcu30bfu30fcu3092u4f5cu6210
user_profile_router = APIRouter(
    tags=["Customer - User Profile"],
    dependencies=[Depends(get_current_user)]
)

# u30e6u30fcu30b6u30fcu30d7u30edu30d5u30a3u30fcu30ebu95a2u9023u306eu30a8u30f3u30c9u30ddu30a4u30f3u30c8u3092u30a4u30f3u30afu30ebu30fcu30c9
import app.features.customer.user_profile.endpoints.user_profile as user_profile_api_router
user_profile_router.include_router(user_profile_api_router.router, prefix="", tags=["Customer - User Profile API"])
