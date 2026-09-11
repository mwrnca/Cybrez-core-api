from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie

from app.core.security import create_refresh_token, decode_refresh_token
from app.config.settings import settings
from app.models.refresh_session import RefreshSession


def register_and_login(client, email):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "Auth User",
        },
    )

    return client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )


def refresh_cookie(response):
    cookies = SimpleCookie()
    cookies.load(response.headers["set-cookie"])
    return cookies[settings.REFRESH_COOKIE_NAME].value


def test_register(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
        },
    )

    print(response.status_code)
    print(response.json())

    assert response.status_code == 201


def test_register_duplicate_email(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "full_name": "User",
        },
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "full_name": "User",
        },
    )

    assert response.status_code == 400


def test_login(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123",
            "full_name": "Login User",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "password123",
        },
    )

    print(response.status_code)
    print(response.json())

    assert response.status_code == 200


def test_login_invalid_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "password123",
            "full_name": "Wrong Password User",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrongpass@example.com",
            "password": "wrongpassword",
        },
    )

    print(response.status_code)
    print(response.json())

    assert response.status_code == 401


def test_login_creates_refresh_session(client, db):
    response = register_and_login(client, "session@example.com")

    assert response.status_code == 200
    refresh_session = db.query(RefreshSession).one()
    refresh_token = refresh_cookie(response)
    payload = decode_refresh_token(refresh_token)

    assert str(refresh_session.public_id) == payload["jti"]
    assert refresh_session.token_hash != refresh_token
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "SameSite=lax" in response.headers["set-cookie"]
    assert "Path=/api/v1/auth" in response.headers["set-cookie"]


def test_login_cookie_is_secure_by_default(client, monkeypatch):
    monkeypatch.setattr(settings, "REFRESH_COOKIE_SECURE", True)
    response = register_and_login(client, "secure-cookie@example.com")

    assert "Secure" in response.headers["set-cookie"]


def test_valid_refresh_succeeds(client):
    login_response = register_and_login(client, "refresh@example.com")

    response = client.post(
        "/api/v1/auth/refresh",
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert refresh_cookie(response)


def test_old_refresh_token_cannot_be_reused_after_rotation(client):
    login_response = register_and_login(client, "rotation@example.com")
    old_refresh_token = refresh_cookie(login_response)

    response = client.post(
        "/api/v1/auth/refresh",
    )
    assert response.status_code == 200

    client.cookies.set(
        settings.REFRESH_COOKIE_NAME,
        old_refresh_token,
        path="/api/v1/auth",
    )
    response = client.post(
        "/api/v1/auth/refresh",
    )

    assert response.status_code == 401


def test_nonexistent_refresh_session_returns_401(client):
    login_response = register_and_login(client, "missing-session@example.com")
    user_id = decode_refresh_token(refresh_cookie(login_response))["sub"]
    token_without_session = create_refresh_token(user_id)
    client.cookies.set(settings.REFRESH_COOKIE_NAME, token_without_session)

    response = client.post(
        "/api/v1/auth/refresh",
    )

    assert response.status_code == 401


def test_revoked_refresh_session_returns_401(client, db):
    login_response = register_and_login(client, "revoked@example.com")
    refresh_session = db.query(RefreshSession).one()
    refresh_session.revoked_at = datetime.now(timezone.utc)
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
    )

    assert response.status_code == 401


def test_expired_refresh_session_returns_401(client, db):
    login_response = register_and_login(client, "expired@example.com")
    refresh_session = db.query(RefreshSession).one()
    refresh_session.expires_at = datetime.now(timezone.utc) - timedelta(
        minutes=1
    )
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
    )

    assert response.status_code == 401


def test_tampered_refresh_token_returns_401(client):
    login_response = register_and_login(client, "tampered@example.com")
    refresh_token = refresh_cookie(login_response)
    tampered_token = refresh_token[:-1] + (
        "a" if refresh_token[-1] != "a" else "b"
    )

    client.cookies.set(settings.REFRESH_COOKIE_NAME, tampered_token)
    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401


def test_refresh_session_cannot_be_used_for_another_user(client, db):
    login_response = register_and_login(client, "bound@example.com")
    other_login_response = register_and_login(client, "other@example.com")
    other_user_id = decode_refresh_token(
        refresh_cookie(other_login_response)
    )["sub"]
    refresh_session = (
        db.query(RefreshSession)
        .filter(
            RefreshSession.public_id
            == decode_refresh_token(refresh_cookie(login_response))["jti"]
        )
        .one()
    )
    refresh_session.user_id = other_user_id
    db.commit()
    client.cookies.set(
        settings.REFRESH_COOKIE_NAME,
        refresh_cookie(login_response),
        path="/api/v1/auth",
    )

    response = client.post(
        "/api/v1/auth/refresh",
    )

    assert response.status_code == 401


def test_logout_revokes_refresh_session(client, db):
    login_response = register_and_login(client, "logout@example.com")
    tokens = login_response.json()

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert f"{settings.REFRESH_COOKIE_NAME}=" in response.headers[
        "set-cookie"
    ]
    assert "Max-Age=0" in response.headers["set-cookie"]
    assert db.query(RefreshSession).one().revoked_at is not None

    response = client.post(
        "/api/v1/auth/refresh",
    )
    assert response.status_code == 401


def test_logout_rejects_another_users_refresh_token(client):
    first_login = register_and_login(client, "logout-first@example.com")
    second_login = register_and_login(client, "logout-second@example.com")

    response = client.post(
        "/api/v1/auth/logout",
        headers={
            "Authorization": (
                f"Bearer {first_login.json()['access_token']}"
            )
        },
    )

    assert response.status_code == 401


def test_inactive_user_cannot_refresh(client, db):
    login_response = register_and_login(client, "inactive@example.com")
    user = db.query(RefreshSession).one().user
    user.is_active = False
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
    )

    assert response.status_code == 401


def test_deleted_user_cannot_refresh(client, db):
    login_response = register_and_login(client, "deleted@example.com")
    user = db.query(RefreshSession).one().user
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
    )

    assert response.status_code == 401


def test_access_token_authentication_still_works(client):
    login_response = register_and_login(client, "access-token@example.com")

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": (
                f"Bearer {login_response.json()['access_token']}"
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "access-token@example.com"