import base64
import hashlib
import hmac
import json
import time
from typing import Any

import httpx
from fastapi import HTTPException, Request, Response, status

from begamer_worker.schemas import SessionUser

SESSION_COOKIE = "begamer_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 30


def env_text(env: Any, name: str, default: str | None = None) -> str | None:
    value = getattr(env, name, None)
    if value is None:
        return default
    text = str(value).strip()
    return text if text and text not in {"undefined", "null"} else default


def auth_required(env: Any) -> bool:
    return (env_text(env, "AUTH_REQUIRED", "true") or "true").casefold() == "true"


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _session_secret(env: Any) -> str:
    secret = env_text(env, "SESSION_SECRET")
    if secret is None or len(secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="登录尚未完成配置。",
        )
    return secret


def create_session(user: SessionUser, env: Any) -> str:
    payload = {
        "sub": user.sub,
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "exp": int(time.time()) + SESSION_MAX_AGE,
    }
    body = _encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _encode(
        hmac.new(_session_secret(env).encode(), body.encode(), hashlib.sha256).digest()
    )
    return f"{body}.{signature}"


def read_session(token: str | None, env: Any) -> SessionUser | None:
    if not token or "." not in token:
        return None
    body, signature = token.split(".", 1)
    expected = _encode(
        hmac.new(_session_secret(env).encode(), body.encode(), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        payload = json.loads(_decode(body))
        if int(payload["exp"]) <= int(time.time()):
            return None
        return SessionUser(
            sub=str(payload["sub"]),
            email=str(payload["email"]),
            display_name=str(payload["display_name"]),
            avatar_url=payload.get("avatar_url"),
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def request_env(request: Request) -> Any:
    return request.scope["env"]


def current_user(request: Request) -> SessionUser:
    env = request_env(request)
    if not auth_required(env):
        return SessionUser(
            sub="local-development",
            email="local@begamer.invalid",
            display_name="Night Player",
        )
    user = read_session(request.cookies.get(SESSION_COOKIE), env)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先使用 Google 登录。",
        )
    allowed_email = env_text(env, "ALLOWED_GOOGLE_EMAIL")
    if allowed_email is None or user.email.casefold() != allowed_email.casefold():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="此账号没有访问权限。")
    return user


async def verify_google_credential(credential: str, env: Any) -> SessionUser:
    client_id = env_text(env, "GOOGLE_CLIENT_ID")
    allowed_email = env_text(env, "ALLOWED_GOOGLE_EMAIL")
    if client_id is None or allowed_email is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google 登录尚未完成配置。",
        )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": credential},
            )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google 登录凭据无效或已过期。",
        ) from error

    email = str(payload.get("email", ""))
    verified = str(payload.get("email_verified", "")).casefold() == "true"
    issuer = str(payload.get("iss", ""))
    if (
        str(payload.get("aud", "")) != client_id
        or not verified
        or issuer not in {"accounts.google.com", "https://accounts.google.com"}
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google 登录校验失败。",
        )
    if email.casefold() != allowed_email.casefold():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="此账号没有访问权限。")
    subject = str(payload.get("sub", ""))
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google 账号信息不完整。",
        )
    return SessionUser(
        sub=subject,
        email=email,
        display_name=str(payload.get("name") or email.split("@", 1)[0]),
        avatar_url=str(payload["picture"]) if payload.get("picture") else None,
    )


def attach_session(response: Response, user: SessionUser, env: Any) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        create_session(user, env),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=auth_required(env),
        samesite="lax",
        path="/",
    )


def clear_session(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/", samesite="lax")
