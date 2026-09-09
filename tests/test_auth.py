from datetime import datetime, timedelta, timezone

from app.core.security import create_refresh_token, decode_refresh_token
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
    payload = decode_refresh_token(response.json()["refresh_token"])

    assert str(refresh_session.public_id) == payload["jti"]
    assert refresh_session.token_hash != response.json()["refresh_token"]


def test_valid_refresh_succeeds(client):
    login_response = register_and_login(client, "refresh@example.com")

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_response.json()["refresh_token"]},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]


def test_old_refresh_token_cannot_be_reused_after_rotation(client):
    login_response = register_and_login(client, "rotation@example.com")
    old_refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert response.status_code == 200

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert response.status_code == 401


def test_nonexistent_refresh_session_returns_401(client):
    login_response = register_and_login(client, "missing-session@example.com")
    user_id = decode_refresh_token(
        login_response.json()["refresh_token"]
    )["sub"]
    token_without_session = create_refresh_token(user_id)

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_without_session},
    )

    assert response.status_code == 401


def test_revoked_refresh_session_returns_401(client, db):
    login_response = register_and_login(client, "revoked@example.com")
    refresh_session = db.query(RefreshSession).one()
    refresh_session.revoked_at = datetime.now(timezone.utc)
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_response.json()["refresh_token"]},
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
        json={"refresh_token": login_response.json()["refresh_token"]},
    )

    assert response.status_code == 401


def test_tampered_refresh_token_returns_401(client):
    login_response = register_and_login(client, "tampered@example.com")
    refresh_token = login_response.json()["refresh_token"]
    tampered_token = refresh_token[:-1] + (
        "a" if refresh_token[-1] != "a" else "b"
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tampered_token},
    )

    assert response.status_code == 401


def test_refresh_session_cannot_be_used_for_another_user(client, db):
    login_response = register_and_login(client, "bound@example.com")
    other_login_response = register_and_login(client, "other@example.com")
    other_user_id = decode_refresh_token(
        other_login_response.json()["refresh_token"]
    )["sub"]
    refresh_session = (
        db.query(RefreshSession)
        .filter(RefreshSession.public_id == decode_refresh_token(
            login_response.json()["refresh_token"]
        )["jti"])
        .one()
    )
    refresh_session.user_id = other_user_id
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_response.json()["refresh_token"]},
    )

    assert response.status_code == 401


def test_logout_revokes_refresh_session(client, db):
    login_response = register_and_login(client, "logout@example.com")
    tokens = login_response.json()

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 200
    assert db.query(RefreshSession).one().revoked_at is not None

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
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
        json={"refresh_token": second_login.json()["refresh_token"]},
    )

    assert response.status_code == 401


def test_inactive_user_cannot_refresh(client, db):
    login_response = register_and_login(client, "inactive@example.com")
    user = db.query(RefreshSession).one().user
    user.is_active = False
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_response.json()["refresh_token"]},
    )

    assert response.status_code == 401


def test_deleted_user_cannot_refresh(client, db):
    login_response = register_and_login(client, "deleted@example.com")
    user = db.query(RefreshSession).one().user
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_response.json()["refresh_token"]},
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