import time
from collections import defaultdict
from threading import Lock


class LoginRateLimiter:
    """
    In-memory rate limiter for login attempts.
    Tracks failed attempts per email and blocks after max_attempts within the window.
    """

    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_blocked(self, email: str) -> bool:
        """Check if the email is currently blocked due to too many attempts."""
        with self._lock:
            self._cleanup(email)
            return len(self._attempts[email]) >= self._max_attempts

    def record_failed_attempt(self, email: str) -> None:
        """Record a failed login attempt for the given email."""
        with self._lock:
            self._cleanup(email)
            self._attempts[email].append(time.time())

    def reset(self, email: str) -> None:
        """Reset attempts after a successful login."""
        with self._lock:
            self._attempts.pop(email, None)

    def _cleanup(self, email: str) -> None:
        """Remove expired attempts outside the time window."""
        cutoff = time.time() - self._window_seconds
        self._attempts[email] = [t for t in self._attempts[email] if t > cutoff]


# Singleton instance used across the application
login_rate_limiter = LoginRateLimiter(max_attempts=5, window_seconds=60)
