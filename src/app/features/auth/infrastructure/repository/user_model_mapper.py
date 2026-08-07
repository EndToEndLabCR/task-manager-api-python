from src.app.features.auth.domain.entities.user_entity import UserEntity
from src.app.features.auth.domain.value_objects.email import Email
from src.app.features.auth.infrastructure.models.user_model import UserModel
from src.shared.domain.value_objects.entity_id import EntityId


def map_model_to_entity(user_model: UserModel) -> UserEntity:
    """Maps a user model to a user entity."""

    return UserEntity(
        id=EntityId(user_model.id),
        email=Email(value=user_model.email),
        username=user_model.username,
        password_hash=user_model.password_hash,
        is_verified=user_model.is_verified,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
    )
