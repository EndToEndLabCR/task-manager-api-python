from fastapi import APIRouter, Depends, HTTPException, status

from src.app.features.auth.application.dtos.user_dto import MessageResponse, PasswordResetRequestDTO, PasswordResetConfirmDTO
from src.app.features.auth.application.use_cases.request_password_reset import RequestPasswordResetUseCase
from src.app.features.auth.application.use_cases.confirm_password_reset import ConfirmPasswordResetUseCase
from src.app.features.auth.presentation.web.dependencies import (
    get_request_reset_use_case,
    get_confirm_reset_use_case,
)

router = APIRouter()


@router.post("/request", response_model=MessageResponse)
async def request_reset(
    payload: PasswordResetRequestDTO,
    use_case: RequestPasswordResetUseCase = Depends(get_request_reset_use_case),
) -> MessageResponse:
    try:
        await use_case.execute(payload.email)
        return MessageResponse(message="Reset email sent")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))


@router.post("/confirm", response_model=MessageResponse)
async def confirm_reset(
    payload: PasswordResetConfirmDTO,
    use_case: ConfirmPasswordResetUseCase = Depends(get_confirm_reset_use_case),
) -> MessageResponse:
    try:
        await use_case.execute(payload.token, payload.new_password)
        return MessageResponse(message="Password updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))