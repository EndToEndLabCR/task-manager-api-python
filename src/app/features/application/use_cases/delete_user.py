from src.app.features.application.dtos.user_dto import DeleteResponse
from src.app.features.application.exceptions.user_exception import UserDoesNotExistException
from src.app.features.domain.repositories.user_repository import UserRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class DeleteUserUseCase:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: str) -> DeleteResponse:
        try:
            user_obj_id = EntityId.from_string(user_id)

            deleted = await self.user_repository.delete(user_obj_id)

            if not deleted:
                log.warning(f"User not found for deletion with ID: {user_id}")
                raise UserDoesNotExistException(user_id)

            log.info(f"User deleted successfully: {user_id}")
            return DeleteResponse(message=f"User with ID {user_id} deleted successfully")

        except (ValueError, UserDoesNotExistException):
            raise
        except Exception as e:
            log.error(f"Unexpected error in DeleteUserUseCase: {str(e)}")
            raise