"""
Módulo de seguridad y utilidades de protección de datos para Orbe-Service.
Incluye sanitización de logs, validaciones y SecureLogger.
"""

import hashlib
import logging
import re
from typing import Any, Dict


def sanitize_for_logging(data: Any) -> Any:
    """
    Sanitiza datos sensibles antes de logging.
    Remueve o enmascara tokens, API keys, emails, etc.
    """
    if isinstance(data, str):
        # Enmascarar tokens largos (32+ caracteres hex)
        data = re.sub(r"\b[a-f0-9]{32,}\b", "****TOKEN****", data)
        # Enmascarar API keys (sk-xxx, key-xxx)
        data = re.sub(
            r"\b(sk-|key-|api[_-]?key[_-]?)[a-zA-Z0-9]{20,}\b",
            r"\1****",
            data,
            flags=re.IGNORECASE,
        )
        # Enmascarar emails parcialmente
        data = re.sub(
            r"\b([a-zA-Z0-9_.+-]{2})[a-zA-Z0-9_.+-]*@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b",
            r"\1****@\2",
            data,
        )
        # Enmascarar Bearer tokens
        data = re.sub(r"Bearer\s+[a-zA-Z0-9._-]+", "Bearer ****", data)
        return data

    elif isinstance(data, dict):
        sanitized = {}
        sensitive_keys = {
            "password",
            "token",
            "auth_token",
            "access_token",
            "refresh_token",
            "secret",
            "api_key",
            "openai_api_key",
            "elevenlabs_api_key",
            "access_key",
            "secret_key",
            "authorization",
            "credentials",
        }

        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(value, str) and len(value) > 0:
                    sanitized[key] = value[:4] + "****"
                else:
                    sanitized[key] = "****"
            else:
                sanitized[key] = sanitize_for_logging(value)
        return sanitized

    elif isinstance(data, list):
        return [sanitize_for_logging(item) for item in data]

    return data


def hash_secret(value: str, salt: str = "orbe_secure_salt_2025") -> str:
    """
    Hashea un valor usando SHA-256 con salt.
    Para producción, considerar usar bcrypt o argon2.
    """
    return hashlib.sha256(f"{value}{salt}".encode()).hexdigest()


def verify_hash(
    value: str, hashed_value: str, salt: str = "orbe_secure_salt_2025"
) -> bool:
    """
    Verifica un valor contra su hash.
    """
    return hash_secret(value, salt) == hashed_value


def validate_email(email: str) -> bool:
    """
    Valida formato básico de email.
    """
    if not email or not isinstance(email, str):
        return False

    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_tenant_id(tenant_id: str) -> bool:
    """
    Valida formato de tenant_id (alfanumérico, guiones, underscores).
    """
    if not tenant_id or not isinstance(tenant_id, str):
        return False

    # 3-50 caracteres, alfanumérico con guiones y underscores
    pattern = r"^[a-zA-Z0-9_-]{3,50}$"
    return bool(re.match(pattern, tenant_id.strip()))


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enmascara datos sensibles en un diccionario para respuestas API.
    """
    masked = data.copy()

    sensitive_fields = ["password", "token", "api_key", "secret"]
    for field in sensitive_fields:
        if field in masked:
            del masked[field]

    # Enmascarar email parcialmente
    if "email" in masked and masked["email"]:
        parts = masked["email"].split("@")
        if len(parts) == 2:
            masked["email"] = parts[0][:2] + "****@" + parts[1]

    return masked


class SecureLogger:
    """
    Logger wrapper que sanitiza automáticamente datos sensibles.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def info(self, message: str, *args, **kwargs):
        sanitized_msg = sanitize_for_logging(message)
        self.logger.info(sanitized_msg, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        sanitized_msg = sanitize_for_logging(message)
        self.logger.warning(sanitized_msg, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        sanitized_msg = sanitize_for_logging(message)
        self.logger.error(sanitized_msg, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        sanitized_msg = sanitize_for_logging(message)
        self.logger.debug(sanitized_msg, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        sanitized_msg = sanitize_for_logging(message)
        self.logger.exception(sanitized_msg, *args, **kwargs)


def get_secure_logger(name: str) -> SecureLogger:
    """
    Obtiene un SecureLogger para el módulo especificado.
    """
    return SecureLogger(logging.getLogger(name))
