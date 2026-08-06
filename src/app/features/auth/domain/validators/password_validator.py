import re


class PasswordValidator:
    """
    Domain validator for password complexity rules.
    Rules: min 8 chars, at least one uppercase, one lowercase, one digit.
    """

    MIN_LENGTH = 8
    _UPPERCASE_PATTERN = re.compile(r"[A-Z]")
    _LOWERCASE_PATTERN = re.compile(r"[a-z]")
    _DIGIT_PATTERN = re.compile(r"[0-9]")

    @classmethod
    def validate(cls, password: str) -> None:
        """
        Validates password complexity. Raises ValueError if invalid.

        Args:
            password: The plain-text password to validate.

        Raises:
            ValueError: With a descriptive message if validation fails.
        """
        errors: list[str] = []

        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters long")

        if not cls._UPPERCASE_PATTERN.search(password):
            errors.append("Password must contain at least one uppercase letter")

        if not cls._LOWERCASE_PATTERN.search(password):
            errors.append("Password must contain at least one lowercase letter")

        if not cls._DIGIT_PATTERN.search(password):
            errors.append("Password must contain at least one digit")

        if errors:
            raise ValueError(". ".join(errors))
