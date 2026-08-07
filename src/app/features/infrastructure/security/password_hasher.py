import hashlib
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordHasher:

    def _pre_hash(self, plain_password: str) -> str:
        # Generates a unique, fixed-size SHA-256 hash for the user's password
        return hashlib.sha256(plain_password.encode('utf-8')).hexdigest()

    def hash(self, plain_password: str) -> str:
        # We first hash with SHA-256 and the result is processed by Bcrypt
        return _pwd_context.hash(self._pre_hash(plain_password))

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        # The same to verify
        return _pwd_context.verify(self._pre_hash(plain_password), hashed_password)