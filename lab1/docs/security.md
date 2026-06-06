# Безопасность: хэширование и JWT вручную

По заданию (п.3) аутентификация по JWT реализована **вручную**, без сторонних
библиотек: используется только стандартная библиотека Python
(`hashlib`, `hmac`, `base64`, `json`, `secrets`). Это покрывает создание токена,
проверку подписи и срока действия, а также хэширование паролей.

## Хэширование паролей (PBKDF2-HMAC-SHA256)

Файл [`app/core/security.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/core/security.py):

```python
import base64, hashlib, hmac, secrets

_PBKDF2_ITERATIONS = 260_000
_SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Возвращает строку формата pbkdf2_sha256$iterations$salt$hash."""
    salt = secrets.token_bytes(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        _PBKDF2_ITERATIONS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(dk).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    """Проверка пароля (constant-time сравнение)."""
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
```

## JWT (HS256) — ручная реализация

```python
import base64, hashlib, hmac, json, time
from app.core.config import settings


class JWTError(Exception):
    """Ошибка валидации/декодирования JWT."""


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _sign(signing_input: bytes) -> bytes:
    return hmac.new(settings.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()


def create_access_token(subject, extra=None) -> str:
    """Создаёт подписанный JWT с полями sub, iat, exp."""
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": str(subject), "iat": now,
               "exp": now + settings.access_token_expire_minutes * 60}
    if extra:
        payload.update(extra)

    header_segment = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature_segment = _b64url_encode(_sign(signing_input))
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def decode_access_token(token: str) -> dict:
    """Проверяет подпись и срок действия токена, возвращает payload."""
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

    payload = json.loads(_b64url_decode(payload_segment))
    exp = payload.get("exp")
    if exp is None or int(time.time()) >= int(exp):
        raise JWTError("Срок действия токена истёк")
    return payload
```

## Зависимость аутентификации (ручная)

Файл [`app/api/deps.py`](https://github.com/Makarov1e/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/lab1/app/api/deps.py)
— мы сами читаем заголовок `Authorization`, парсим схему `Bearer`, проверяем токен
и достаём пользователя из БД:

```python
def get_current_user(session: SessionDep, authorization: str | None = Header(None)) -> User:
    credentials_error = HTTPException(401, "Не удалось проверить учётные данные",
                                      headers={"WWW-Authenticate": "Bearer"})
    if not authorization:
        raise credentials_error

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise credentials_error
    token = parts[1]

    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise HTTPException(401, str(exc), headers={"WWW-Authenticate": "Bearer"}) from exc

    user = session.get(User, int(payload.get("sub")))
    if user is None or not user.is_active:
        raise credentials_error
    return user


def require_roles(*roles: UserRole):
    """Фабрика зависимостей RBAC: пропускает только пользователей с нужной ролью."""
    def checker(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(403, "Недостаточно прав для выполнения операции")
        return current_user
    return checker
```

## Проверка (результаты)

| Сценарий | Результат |
|---|---|
| Запрос без токена | `401` |
| Битый/поддельный токен | `401` «Неверная подпись токена» |
| Просроченный токен | `401` «Срок действия токена истёк» |
| Не-админ создаёт задачу | `403` |
| Не-жюри оценивает решение | `403` |
| Повторная оценка тем же жюри | `409` (unique constraint) |
