class TaskNotFoundException(Exception):
    def __init__(self, task_id: str):
        self.message = f"Task with ID {task_id} does not exist."
        super().__init__(self.message)


class TaskAccessDeniedException(Exception):
    def __init__(self, resource_id: str, user_id: str):
        self.message = f"User {user_id} does not have access to resource {resource_id}."
        super().__init__(self.message)
