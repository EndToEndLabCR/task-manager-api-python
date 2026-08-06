# src/app/features/application/use_cases/refresh_token.py
from src.app.features.auth.application.dtos.user_dto import LoginResponse
from src.app.features.auth.infrastructure.security.jwt_provider import JWTProvider


class RefreshTokenUseCase:

    def __init__(self, jwt_provider: JWTProvider):
        self._jwt_provider = jwt_provider

    async def execute(self, refresh_token: str) -> LoginResponse:
        payload = self._jwt_provider.validate_refresh_token(refresh_token)

        if not payload:
            raise ValueError("Invalid or expired refresh token.")

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            raise ValueError("Invalid refresh token payload.")

        new_access_token = self._jwt_provider.create_access_token(user_id=user_id, email=email,)
        new_refresh_token = self._jwt_provider.create_refresh_token(user_id=user_id, email=email,)

        return LoginResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=86400,)