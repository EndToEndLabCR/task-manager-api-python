from src.app.features.auth.domain.repositories.email_verification_repository import EmailVerificationRepository
from src.app.features.auth.domain.repositories.user_repository import UserRepository
from src.app.features.auth.infrastructure.security.reset_token_generator import ResetTokenGenerator
from src.shared.domain.value_objects.entity_id import EntityId


class VerifyEmailUseCase:

    def __init__(
        self,
        email_verification_repository: EmailVerificationRepository,
        user_repository: UserRepository,
        token_generator: ResetTokenGenerator,
    ):
        self._email_verification_repository = email_verification_repository
        self._user_repository = user_repository
        self._token_generator = token_generator

    async def execute(self, raw_token: str) -> None:
        """Verifies a user's email using the provided token."""
        token_hash = self._token_generator.hash(raw_token)
        verification = await self._email_verification_repository.find_by_token_hash(token_hash)

        if not verification or not verification.is_valid:
            raise ValueError("Invalid or expired verification token.")

        user = await self._user_repository.find_by_id(EntityId(verification.user_id))

        if not user:
            raise ValueError("User not found.")

        user.verify_email()
        await self._user_repository.update(user)

        verification.mark_as_used()
        await self._email_verification_repository.update(verification)
