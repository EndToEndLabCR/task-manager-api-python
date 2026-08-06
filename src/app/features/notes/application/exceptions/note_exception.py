class NoteNotFoundException(Exception):
    def __init__(self, note_id: str):
        self.message = f"Note with ID {note_id} does not exist."
        super().__init__(self.message)


class NoteAccessDeniedException(Exception):
    def __init__(self, resource_id: str, user_id: str):
        self.message = f"User {user_id} does not have access to resource {resource_id}."
        super().__init__(self.message)


class NoteAlreadyConvertedException(Exception):
    def __init__(self, note_id: str):
        self.message = f"Note {note_id} has already been converted and cannot be converted again."
        super().__init__(self.message)
