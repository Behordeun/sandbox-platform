import base64
import json
from typing import Any, Dict

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .config import settings


class ConfigEncryption:
    """Encryption utilities for sensitive configuration data."""

    def __init__(self, key: str = None):
        self.key = key or settings.encryption_key
        self._fernet = None

    def _get_fernet(self) -> Fernet:
        """Get or create Fernet instance."""
        if self._fernet is None:
            # Derive key from password
            # Use a random, securely stored salt from settings or environment variable
            salt = getattr(settings, "encryption_salt", None)
            if not salt:
                raise ValueError(
                    "Encryption salt must be set in settings for secure key derivation."
                )
            if isinstance(salt, str):
                salt = salt.encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,  # Secure, unpredictable salt
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.key.encode()))
            self._fernet = Fernet(key)
        return self._fernet

    def encrypt_value(self, value: Any) -> str:
        """Encrypt a configuration value."""
        if value is None:
            return None

        # Convert to JSON string
        json_str = json.dumps(value)

        # Encrypt
        fernet = self._get_fernet()
        encrypted_bytes = fernet.encrypt(json_str.encode())

        # Return base64 encoded string
        return base64.urlsafe_b64encode(encrypted_bytes).decode()

    def decrypt_value(self, encrypted_value: str) -> Any:
        """Decrypt a configuration value."""
        if not encrypted_value:
            return None

        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())

            # Decrypt
            fernet = self._get_fernet()
            decrypted_bytes = fernet.decrypt(encrypted_bytes)

            # Parse JSON
            return json.loads(decrypted_bytes.decode())

        except Exception as e:
            raise ValueError(f"Failed to decrypt value: {e}")

    def encrypt_config(
        self, config: Dict[str, Any], sensitive_keys: list = None
    ) -> Dict[str, Any]:
        """Encrypt sensitive keys in a configuration dictionary."""
        if not sensitive_keys:
            sensitive_keys = [
                "password",
                "secret",
                "key",
                "token",
                "api_key",
                "private_key",
                "certificate",
                "credential",
            ]

        encrypted_config = {}

        for key, value in config.items():
            # Check if key should be encrypted
            should_encrypt = any(
                sensitive_key in key.lower() for sensitive_key in sensitive_keys
            )

            if should_encrypt and value is not None:
                encrypted_config[key] = {
                    "_encrypted": True,
                    "_value": self.encrypt_value(value),
                }
            elif isinstance(value, dict):
                # Recursively encrypt nested dictionaries
                encrypted_config[key] = self.encrypt_config(value, sensitive_keys)
            else:
                encrypted_config[key] = value

        return encrypted_config

    def decrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt encrypted values in a configuration dictionary."""
        decrypted_config = {}

        for key, value in config.items():
            if isinstance(value, dict):
                if value.get("_encrypted"):
                    # Decrypt encrypted value
                    decrypted_config[key] = self.decrypt_value(value["_value"])
                else:
                    # Recursively decrypt nested dictionaries
                    decrypted_config[key] = self.decrypt_config(value)
            else:
                decrypted_config[key] = value

        return decrypted_config

    def is_encrypted_value(self, value: Any) -> bool:
        """Check if a value is encrypted."""
        return (
            isinstance(value, dict)
            and value.get("_encrypted") is True
            and "_value" in value
        )


# Global encryption instance
config_encryption = ConfigEncryption()
