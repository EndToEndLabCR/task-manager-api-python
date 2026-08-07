from src.app.features.domain.entities.email_verification_entity import EmailVerificationEntity
from src.app.features.infrastructure.models.email_verification_model import EmailVerificationTokenModel
from src.shared.domain.value_objects.entity_id import EntityId


def map_model_to_entity(model: EmailVerificationTokenModel) -> EmailVerificationEntity:
    return EmailVerificationEntity(
        id=EntityId(model.id),
        user_id=model.user_id,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
        used_at=model.used_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
