from types import SimpleNamespace

from begamer_worker.auth import create_session, read_session
from begamer_worker.schemas import SessionUser


def test_session_round_trip_and_tamper_rejection() -> None:
    env = SimpleNamespace(SESSION_SECRET="a" * 48)
    user = SessionUser(
        sub="google-subject",
        email="player@example.com",
        display_name="Night Player",
        avatar_url="https://example.com/avatar.png",
    )

    token = create_session(user, env)

    assert read_session(token, env) == user
    assert read_session(f"{token[:-1]}x", env) is None


def test_invalid_session_shape_is_rejected() -> None:
    env = SimpleNamespace(SESSION_SECRET="b" * 48)

    assert read_session(None, env) is None
    assert read_session("not-a-session", env) is None
