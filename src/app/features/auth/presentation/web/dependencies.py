import os
from typing import AsyncGenerator, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config.app_config import AppConfig
from src.app.features.auth.application.dtos.user_dto import UserResponse
from src.app.features.auth.application.use_cases.create_user import CreateUserUseCase
from src.app.features.auth.application.use_cases.delete_user import DeleteUserUseCase
from src.app.features.auth.application.use_cases.get_user_by_id import GetUserByIdUseCase
from src.app.features.auth.application.use_cases.login_user import LoginUseCase
from src.app.features.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from src.app.features.auth.application.use_cases.request_password_reset import RequestPasswordResetUseCase
from src.app.features.auth.application.use_cases.confirm_password_reset import ConfirmPasswordResetUseCase
from src.app.features.auth.application.use_cases.send_verification_email import SendVerificationEmailUseCase
from src.app.features.auth.application.use_cases.verify_email import VerifyEmailUseCase
from src.app.features.auth.infrastructure.email.resend_email_sender import ResendEmailSender
from src.app.features.auth.infrastructure.repository.user_repository_impl import UserRepositoryImpl
from src.app.features.auth.infrastructure.repository.password_reset_repository_impl import PasswordResetRepositoryImpl
from src.app.features.auth.infrastructure.repository.email_verification_repository_impl import EmailVerificationRepositoryImpl
from src.app.features.auth.infrastructure.security.password_hasher import PasswordHasher
from src.app.features.auth.infrastructure.security.jwt_provider import JWTProvider
from src.app.features.auth.infrastructure.security.reset_token_generator import ResetTokenGenerator
from src.shared.infrastructure.config.postgres_db_conn import PostgresDbConnection
from src.shared.utils.config_util import get_config_value

app_config: dict = AppConfig.instance().config
http_bearer = HTTPBearer()


# --- Infrastructure ---

async def get_database_session() -> AsyncGenerator[Any, Any]:
    postgres_config = get_config_value(app_config, "postgres", {})
    db = PostgresDbConnection(postgres_config)

    async with db.get_session() as session:
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_database_session),
) -> UserRepositoryImpl:
    return UserRepositoryImpl(session)


async def get_password_reset_repository(
    session: AsyncSession = Depends(get_database_session),
) -> PasswordResetRepositoryImpl:
    return PasswordResetRepositoryImpl(session)


async def get_email_verification_repository(
    session: AsyncSession = Depends(get_database_session),
) -> EmailVerificationRepositoryImpl:
    return EmailVerificationRepositoryImpl(session)


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_provider() -> JWTProvider:
    secret = os.getenv("SECRET_KEY", "default-secret")
    return JWTProvider(secret_key=secret)


def get_reset_token_generator() -> ResetTokenGenerator:
    return ResetTokenGenerator()


def get_email_sender() -> ResendEmailSender:
    return ResendEmailSender()


# --- Use Cases ---

async def get_send_verification_email_use_case(
    email_verification_repository: EmailVerificationRepositoryImpl = Depends(get_email_verification_repository),
    token_generator: ResetTokenGenerator = Depends(get_reset_token_generator),
    email_sender: ResendEmailSender = Depends(get_email_sender),
) -> SendVerificationEmailUseCase:
    return SendVerificationEmailUseCase(
        email_verification_repository=email_verification_repository,
        token_generator=token_generator,
        email_sender=email_sender,
    )


async def get_verify_email_use_case(
    email_verification_repository: EmailVerificationRepositoryImpl = Depends(get_email_verification_repository),
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
    token_generator: ResetTokenGenerator = Depends(get_reset_token_generator),
) -> VerifyEmailUseCase:
    return VerifyEmailUseCase(
        email_verification_repository=email_verification_repository,
        user_repository=user_repository,
        token_generator=token_generator,
    )


async def get_register_user_use_case(
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    send_verification_email_use_case: SendVerificationEmailUseCase = Depends(get_send_verification_email_use_case),
) -> CreateUserUseCase:
    return CreateUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        send_verification_email_use_case=send_verification_email_use_case,
    )


async def get_login_use_case(
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> LoginUseCase:
    return LoginUseCase(user_repository, password_hasher, jwt_provider)


async def get_refresh_token_use_case(
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(jwt_provider)


async def get_user_by_id_use_case(
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
) -> GetUserByIdUseCase:
    return GetUserByIdUseCase(user_repository)


async def get_delete_user_use_case(
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
) -> DeleteUserUseCase:
    return DeleteUserUseCase(user_repository)


async def get_request_reset_use_case(
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
    password_reset_repository: PasswordResetRepositoryImpl = Depends(get_password_reset_repository),
    token_generator: ResetTokenGenerator = Depends(get_reset_token_generator),
    email_sender: ResendEmailSender = Depends(get_email_sender),
) -> RequestPasswordResetUseCase:
    return RequestPasswordResetUseCase(
        user_repository=user_repository,
        password_reset_repository=password_reset_repository,
        token_generator=token_generator,
        email_sender=email_sender,
    )


async def get_confirm_reset_use_case(
    user_repository: UserRepositoryImpl = Depends(get_user_repository),
    password_reset_repository: PasswordResetRepositoryImpl = Depends(get_password_reset_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_generator: ResetTokenGenerator = Depends(get_reset_token_generator),
) -> ConfirmPasswordResetUseCase:
    return ConfirmPasswordResetUseCase(
        user_repository=user_repository,
        password_reset_repository=password_reset_repository,
        password_hasher=password_hasher,
        token_generator=token_generator,
    )


# --- Auth ---

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    get_user_by_id: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
    jwt_provider: JWTProvider = Depends(get_jwt_provider),
) -> UserResponse:
    payload = jwt_provider.validate_access_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    try:
        return await get_user_by_id.execute(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
