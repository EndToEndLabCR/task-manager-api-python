class ProjectNotFoundException(Exception):
    """Exception raised when a project is not found."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.message = f"Project with ID {self.project_id} does not exist."
        super().__init__(self.message)


class ProjectAccessDeniedException(Exception):
    """Exception raised when a user attempts to access a project they do not own."""

    def __init__(self, project_id: str, user_id: str):
        self.project_id = project_id
        self.user_id = user_id
        self.message = (
            f"User {self.user_id} does not have access to project {self.project_id}."
        )
        super().__init__(self.message)


class ProjectNameAlreadyExistsException(Exception):
    """Exception raised when a user already has a project with the same name."""

    def __init__(self, name: str):
        self.name = name
        self.message = f"A project named '{self.name}' already exists."
        super().__init__(self.message)
