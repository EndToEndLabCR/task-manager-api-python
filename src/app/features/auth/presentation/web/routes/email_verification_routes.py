from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from src.app.features.auth.application.dtos.user_dto import MessageResponse
from src.app.features.auth.application.use_cases.verify_email import VerifyEmailUseCase
from src.app.features.auth.presentation.web.dependencies import get_verify_email_use_case


class VerifyEmailRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    token: str


router = APIRouter()


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    use_case: VerifyEmailUseCase = Depends(get_verify_email_use_case),
) -> MessageResponse:
    try:
        await use_case.execute(payload.token)
        return MessageResponse(message="Email verified successfully")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
