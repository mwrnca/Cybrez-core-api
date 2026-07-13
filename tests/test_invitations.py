from datetime import datetime, timedelta, timezone

from app.repositories.invitation_repository import InvitationRepository


def create_user(client, email, name):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": name,
        },
    )


def login(client, email):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )
    return response.json()["access_token"]


def auth_header(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def create_organization(client, token):
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Cybrez",
            "slug": "cybrez",
            "description": "Testing",
            "logo_url": None,
        },
        headers=auth_header(token),
    )

    return response.json()["id"]


def test_create_invitation(client):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    token = login(
        client,
        "owner@example.com",
    )

    organization_id = create_organization(
        client,
        token,
    )

    response = client.post(
        f"/api/v1/invitations/{organization_id}/invite",
        json={
            "email": "invitee@example.com",
            "role": "member",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert response.json()["email"] == "invitee@example.com"


def test_accept_invitation(client, db):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    owner_token = login(
        client,
        "owner@example.com",
    )

    organization_id = create_organization(
        client,
        owner_token,
    )

    invitation = client.post(
        f"/api/v1/invitations/{organization_id}/invite",
        json={
            "email": "member@example.com",
            "role": "member",
        },
        headers=auth_header(owner_token),
    ).json()

    create_user(
        client,
        "member@example.com",
        "Member",
    )

    member_token = login(
        client,
        "member@example.com",
    )

    response = client.post(
        f"/api/v1/invitations/accept/{invitation['token']}",
        headers=auth_header(member_token),
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_accept_invalid_token(client):

    create_user(
        client,
        "member@example.com",
        "Member",
    )

    token = login(
        client,
        "member@example.com",
    )

    response = client.post(
        "/api/v1/invitations/accept/invalidtoken",
        headers=auth_header(token),
    )

    assert response.status_code == 404


def test_accept_expired_invitation(client, db):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    owner_token = login(
        client,
        "owner@example.com",
    )

    organization_id = create_organization(
        client,
        owner_token,
    )

    invitation = client.post(
        f"/api/v1/invitations/{organization_id}/invite",
        json={
            "email": "expired@example.com",
            "role": "member",
        },
        headers=auth_header(owner_token),
    ).json()

    invite = InvitationRepository.get_by_token(
        db,
        invitation["token"],
    )

    invite.expires_at = datetime.now(
        timezone.utc
    ) - timedelta(days=1)

    db.commit()

    create_user(
        client,
        "expired@example.com",
        "Expired",
    )

    token = login(
        client,
        "expired@example.com",
    )

    response = client.post(
        f"/api/v1/invitations/accept/{invitation['token']}",
        headers=auth_header(token),
    )

    assert response.status_code == 400


def test_accept_same_invitation_twice(client):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    owner_token = login(
        client,
        "owner@example.com",
    )

    organization_id = create_organization(
        client,
        owner_token,
    )

    invitation = client.post(
        f"/api/v1/invitations/{organization_id}/invite",
        json={
            "email": "member@example.com",
            "role": "member",
        },
        headers=auth_header(owner_token),
    ).json()

    create_user(
        client,
        "member@example.com",
        "Member",
    )

    member_token = login(
        client,
        "member@example.com",
    )

    client.post(
        f"/api/v1/invitations/accept/{invitation['token']}",
        headers=auth_header(member_token),
    )

    response = client.post(
        f"/api/v1/invitations/accept/{invitation['token']}",
        headers=auth_header(member_token),
    )

    assert response.status_code == 400