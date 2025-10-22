import secrets
import string
from typing import Protocol


class IShortCodeGenerator(Protocol):
    """Interface for short code generation strategies."""

    def generate(self, length: int = 6) -> str:
        """Generate a short code."""
        ...


class RandomShortCodeGenerator:
    """Generates random alphanumeric short codes."""

    def __init__(self) -> None:
        # Characters to use: alphanumeric (avoiding similar-looking characters)
        # Excluding: 0, O, I, l to avoid confusion
        self.characters = string.ascii_letters + string.digits
        self.characters = (
            self.characters.replace("0", "")
            .replace("O", "")
            .replace("I", "")
            .replace("l", "")
        )

    def generate(self, length: int = 6) -> str:
        """
        Generate a random short code.

        Args:
            length: Length of the short code (default: 6)

        Returns:
            A random alphanumeric string
        """
        return "".join(secrets.choice(self.characters) for _ in range(length))


# Default generator instance
default_generator = RandomShortCodeGenerator()
