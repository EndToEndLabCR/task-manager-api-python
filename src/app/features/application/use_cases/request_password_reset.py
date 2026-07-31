from datetime import datetime, timedelta, timezone

from src.app.features.domain.entities.password_reset_entity import PasswordResetEntity
from src.app.features.domain.repositories.password_reset_repository import PasswordResetRepository
from src.app.features.domain.repositories.user_repository import UserRepository
from src.app.features.domain.value_objects.email import Email
from src.app.features.infrastructure.email.resend_email_sender import ResendEmailSender
from src.app.features.infrastructure.security.reset_token_generator import ResetTokenGenerator
from src.shared.domain.value_objects.entity_id import EntityId

MAX_REQUESTS_PER_HOUR = 3


class RequestPasswordResetUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_reset_repository: PasswordResetRepository,
        token_generator: ResetTokenGenerator,
        email_sender: ResendEmailSender,
    ):
        self._user_repository = user_repository
        self._password_reset_repository = password_reset_repository
        self._token_generator = token_generator
        self._email_sender = email_sender

    async def execute(self, email: str) -> None:
        email_vo = Email(email.lower().strip())
        user = await self._user_repository.find_by_email(email_vo)

        if not user:
            return

        since = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_requests = await self._password_reset_repository.count_recent_requests(user.id.value, since,)

        if recent_requests >= MAX_REQUESTS_PER_HOUR:
            raise ValueError("Too many reset requests. Please try again later.")

        reset_token = self._token_generator.generate()

        reset_entity = PasswordResetEntity(
            id=EntityId.generate(),
            user_id=user.id.value,
            token_hash=reset_token.token_hash,
            expires_at=reset_token.expires_at,
        )

        await self._password_reset_repository.save(reset_entity)
        await self._email_sender.send_password_reset(str(email_vo), reset_token.raw_token)