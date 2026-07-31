from src.app.features.domain.entities.password_reset_entity import PasswordResetEntity
from src.app.features.infrastructure.models.password_reset_model import PasswordResetTokenModel
from src.shared.domain.value_objects.entity_id import EntityId


def map_model_to_entity(model: PasswordResetTokenModel) -> PasswordResetEntity:
    return PasswordResetEntity(
        id=EntityId(model.id),
        user_id=model.user_id,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
        used_at=model.used_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
