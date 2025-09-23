from typing import Annotated

from clerk_backend_api import AuthenticateRequestOptions, Requestish
from fastapi import HTTPException, Depends

from src.core.config import clerk_sdk, settings
from src.schemas.auth import UserData

def authenticate_and_get_user_details(request: Requestish) -> UserData:
    try:
        request_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=settings.clerk_authorized_parties,
                jwt_key=settings.clerk_jwt_key,
            )
        )
        if not request_state.is_signed_in:
            raise HTTPException(status_code=401, detail='Invalid token')

        user_id = request_state.payload.get('sub')

        return UserData(user_id=user_id)
    except Exception as e:
        # TODO: Error handling and logging
        raise HTTPException(status_code=500, detail=str(e))

auth_dependency = Annotated[UserData, Depends(authenticate_and_get_user_details)]