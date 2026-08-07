from datetime import datetime, timedelta, timezone

from src.app.features.auth.domain.entities.email_verification_entity import EmailVerificationEntity
from src.app.features.auth.domain.repositories.email_verification_repository import EmailVerificationRepository
from src.app.features.auth.infrastructure.email.resend_email_sender import ResendEmailSender
from src.app.features.auth.infrastructure.security.reset_token_generator import ResetTokenGenerator
from src.shared.domain.value_objects.entity_id import EntityId

VERIFICATION_TOKEN_EXPIRY_HOURS = 24


class SendVerificationEmailUseCase:

    def __init__(
        self,
        email_verification_repository: EmailVerificationRepository,
        token_generator: ResetTokenGenerator,
        email_sender: ResendEmailSender,
    ):
        self._email_verification_repository = email_verification_repository
        self._token_generator = token_generator
        self._email_sender = email_sender

    async def execute(self, user_id: str, email: str) -> None:
        """Generates a verification token and sends the verification email."""
        from uuid import UUID

        token_data = self._token_generator.generate()

        entity = EmailVerificationEntity(
            id=EntityId.generate(),
            user_id=UUID(user_id),
            token_hash=token_data.token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=VERIFICATION_TOKEN_EXPIRY_HOURS),
        )

        await self._email_verification_repository.save(entity)
        await self._email_sender.send_verification_email(email, token_data.raw_token)
