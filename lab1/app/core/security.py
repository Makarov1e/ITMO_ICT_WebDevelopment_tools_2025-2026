"""Безопасность: хэширование паролей и ручная реализация JWT.

Согласно заданию (п.3 — аутентификация по JWT) реализовано вручную,
без сторонних библиотек: используется только стандартная библиотека Python
(hashlib, hmac, base64, json, secrets). Это покрывает и создание, и проверку
токена, и хэширование паролей.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.core.config import settings

# ---------------------------------------------------------------------------
# Хэширование паролей (PBKDF2-HMAC-SHA256, стандартная библиотека)
# ---------------------------------------------------------------------------
_PBKDF2_ITERATIONS = 260_000
_SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Возвращает строку формата pbkdf2_sha256$iterations$salt$hash (как в Django)."""
    salt = secrets.token_bytes(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        _PBKDF2_ITERATIONS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(dk).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    """Проверяет пароль против сохранённого хэша (constant-time сравнение)."""
    try:
        algorithm, iterations, salt_b64, hash_b64 = stored.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(dk, expected)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# JWT (HS256) — ручная реализация на base64url + HMAC-SHA256
# ---------------------------------------------------------------------------
class JWTError(Exception):
    """Ошибка валидации/декодирования JWT."""


def _b64url_encode(data: bytes) -> str:
    """base64url без padding (как требует спецификация JWT)."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _sign(signing_input: bytes) -> bytes:
    return hmac.new(settings.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()


def create_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
    """Создаёт подписанный JWT с полями sub, iat, exp."""
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + settings.access_token_expire_minutes * 60,
    }
    if extra:
        payload.update(extra)

    header_segment = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature_segment = _b64url_encode(_sign(signing_input))
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def decode_access_token(token: str) -> dict[str, Any]:
    """Проверяет подпись и срок действия токена, возвращает payload.

    Бросает JWTError при любой проблеме. Это «ручная» аутентификация — никакой
    сторонней библиотеки JWT здесь не используется.
    """
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError as exc:
        raise JWTError("Некорректный формат токена") from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected_sig = _sign(signing_input)
    try:
        actual_sig = _b64url_decode(signature_segment)
    except (ValueError, TypeError) as exc:
        raise JWTError("Некорректная подпись") from exc

    # Сравнение подписи в постоянное время — защита от timing-атак
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise JWTError("Неверная подпись токена")

    try:
        payload = json.loads(_b64url_decode(payload_segment))
    except (ValueError, TypeError) as exc:
        raise JWTError("Некорректный payload") from exc

    exp = payload.get("exp")
    if exp is None or int(time.time()) >= int(exp):
        raise JWTError("Срок действия токена истёк")

    return payload
