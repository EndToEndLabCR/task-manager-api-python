from src.app.features.domain.entities.user_entity import UserEntity
from src.app.features.domain.repositories.user_repository import UserRepository
from src.app.features.domain.validators.password_validator import PasswordValidator
from src.app.features.domain.value_objects.email import Email
from src.app.features.application.dtos.user_dto import UserCreateRequest, UserResponse
from src.app.features.application.dtos.user_dto_mapper import map_entity_to_dto_user
from src.app.features.application.exceptions.user_exception import UserAlreadyExistsException
from src.app.features.application.use_cases.send_verification_email import SendVerificationEmailUseCase
from src.app.features.infrastructure.security.password_hasher import PasswordHasher
from src.shared.domain.value_objects.entity_id import EntityId


class CreateUserUseCase:

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        send_verification_email_use_case: SendVerificationEmailUseCase,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._send_verification_email = send_verification_email_use_case

    async def execute(self, payload: UserCreateRequest) -> UserResponse:
        PasswordValidator.validate(payload.password)

        email_vo = Email(payload.email.lower().strip())

        if await self._user_repository.find_by_email(email_vo):
            raise UserAlreadyExistsException(f"Email already registered: {payload.email}")

        if await self._user_repository.find_by_username(payload.username):
            raise UserAlreadyExistsException(f"Username already taken: {payload.username}")

        user = UserEntity(
            id=EntityId.generate(),
            email=email_vo,
            username=payload.username,
            password_hash=self._password_hasher.hash(payload.password),
        )

        saved_user = await self._user_repository.save(user)

        await self._send_verification_email.execute(
            user_id=str(saved_user.id),
            email=str(saved_user.email),
        )

        return map_entity_to_dto_user(saved_user)
