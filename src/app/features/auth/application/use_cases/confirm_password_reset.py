from src.app.features.auth.domain.repositories.password_reset_repository import PasswordResetRepository
from src.app.features.auth.domain.repositories.user_repository import UserRepository
from src.app.features.auth.domain.validators.password_validator import PasswordValidator
from src.app.features.auth.infrastructure.security.password_hasher import PasswordHasher
from src.app.features.auth.infrastructure.security.reset_token_generator import ResetTokenGenerator
from src.shared.domain.value_objects.entity_id import EntityId


class ConfirmPasswordResetUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_reset_repository: PasswordResetRepository,
        password_hasher: PasswordHasher,
        token_generator: ResetTokenGenerator,
    ):
        self._user_repository = user_repository
        self._password_reset_repository = password_reset_repository
        self._password_hasher = password_hasher
        self._token_generator = token_generator

    async def execute(self, raw_token: str, new_password: str) -> None:
        PasswordValidator.validate(new_password)

        token_hash = self._token_generator.hash(raw_token)
        reset_entity = await self._password_reset_repository.find_by_token_hash(token_hash)

        if not reset_entity or not reset_entity.is_valid:
            raise ValueError("Invalid or expired reset token.")

        user = await self._user_repository.find_by_id(EntityId(reset_entity.user_id))

        if not user:
            raise ValueError("User not found.")

        user.update_password(self._password_hasher.hash(new_password))
        updated_user = await self._user_repository.update(user)

        if not updated_user:
            raise ValueError("User could not be updated.")

        reset_entity.mark_as_used()
        await self._password_reset_repository.update(reset_entity)