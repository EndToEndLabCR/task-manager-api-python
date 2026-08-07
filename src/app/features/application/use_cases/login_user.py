import logging

from src.app.features.domain.repositories.user_repository import UserRepository
from src.app.features.domain.value_objects.email import Email
from src.app.features.application.dtos.user_dto import LoginResponse
from src.app.features.application.exceptions.user_exception import InvalidCredentialsException
from src.app.features.infrastructure.security.password_hasher import PasswordHasher
from src.app.features.infrastructure.security.jwt_provider import JWTProvider
from src.app.features.infrastructure.security.login_rate_limiter import login_rate_limiter

logger = logging.getLogger(__name__)


class TooManyLoginAttemptsException(Exception):
    """Raised when login rate limit is exceeded."""

    def __init__(self, message: str = "Too many login attempts. Please try again later."):
        self.message = message
        super().__init__(self.message)


class LoginUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher, jwt_provider: JWTProvider):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._jwt_provider = jwt_provider

    async def execute(self, email: str, password: str) -> LoginResponse:
        normalized_email = email.lower().strip()

        if login_rate_limiter.is_blocked(normalized_email):
            logger.warning(f"Rate limit exceeded for email: {normalized_email}")
            raise TooManyLoginAttemptsException()

        email_vo = Email(normalized_email)
        user = await self._user_repository.find_by_email(email_vo)

        if not user:
            login_rate_limiter.record_failed_attempt(normalized_email)
            logger.info(f"Failed login attempt for non-existent email: {normalized_email}")
            raise InvalidCredentialsException()

        if not self._password_hasher.verify(password, user.password_hash):
            login_rate_limiter.record_failed_attempt(normalized_email)
            logger.info(f"Failed login attempt (wrong password) for email: {normalized_email}")
            raise InvalidCredentialsException()

        login_rate_limiter.reset(normalized_email)

        user_id = str(user.id)
        user_email = str(user.email)

        access_token = self._jwt_provider.create_access_token(user_id=user_id, email=user_email)
        refresh_token = self._jwt_provider.create_refresh_token(user_id=user_id, email=user_email)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=86400,
        )
