from datetime import datetime, timedelta, timezone

from app.repositories.invitation_repository import InvitationRepository
from app.models.notification import Notification


def invitation_token(db, invitation_id):
    return InvitationRepository.get_by_public_id(db, invitation_id).token


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

    return response.json()["public_id"]


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

    organization_public_id = create_organization(
        client,
        token,
    )

    # Invitee must already have an account -- register them first.
    create_user(
        client,
        "invitee@example.com",
        "Invitee",
    )

    response = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": "invitee@example.com",
            "role": "viewer",
        },
        headers=auth_header(token),
    )

    print(response.status_code)
    print(response.json())

    assert response.status_code == 200
    assert response.json()["email"] == "invitee@example.com"
    assert "token" not in response.json()


def test_create_invitation_no_account(client):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    token = login(
        client,
        "owner@example.com",
    )

    organization_public_id = create_organization(
        client,
        token,
    )

    response = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": "nobody@example.com",
            "role": "viewer",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 400


def test_create_invitation_already_a_member(client):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    token = login(
        client,
        "owner@example.com",
    )

    organization_public_id = create_organization(
        client,
        token,
    )

    # Owner invites themself -- they're already a member.
    response = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": "owner@example.com",
            "role": "viewer",
        },
        headers=auth_header(token),
    )

    assert response.status_code == 400


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

    organization_public_id = create_organization(
        client,
        owner_token,
    )

    create_user(
        client,
        "member@example.com",
        "Member",
    )

    invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": "member@example.com",
            "role": "viewer",
        },
        headers=auth_header(owner_token),
    ).json()
    token = invitation_token(db, invitation["public_id"])

    member_token = login(
        client,
        "member@example.com",
    )

    response = client.post(
        f"/api/v1/invitations/accept/{token}",
        headers=auth_header(member_token),
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_accept_invitation_rejects_wrong_authenticated_user(client, db):
    create_user(client, "owner@example.com", "Owner")
    owner_token = login(client, "owner@example.com")
    organization_public_id = create_organization(client, owner_token)

    create_user(client, "invitee@example.com", "Invitee")
    create_user(client, "other@example.com", "Other")

    invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={"email": "invitee@example.com", "role": "manager"},
        headers=auth_header(owner_token),
    ).json()
    token = invitation_token(db, invitation["public_id"])

    other_token = login(client, "other@example.com")
    response = client.post(
        f"/api/v1/invitations/accept/{token}",
        headers=auth_header(other_token),
    )

    assert response.status_code == 403

    members = client.get(
        f"/api/v1/organizations/{organization_public_id}/members",
        headers=auth_header(owner_token),
    ).json()
    assert all(member["user_email"] != "other@example.com" for member in members)

    invitee_token = login(client, "invitee@example.com")
    accepted = client.post(
        f"/api/v1/invitations/accept/{token}",
        headers=auth_header(invitee_token),
    )

    assert accepted.status_code == 200
    assert accepted.json()["role"] == "manager"


def test_accept_invitation_compares_emails_case_insensitively(client, db):
    create_user(client, "invitee@example.com", "Invitee")
    invitee_token = login(client, "invitee@example.com")

    create_user(client, "owner@example.com", "Owner")
    owner_token = login(client, "owner@example.com")
    organization_public_id = create_organization(client, owner_token)

    invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={"email": "invitee@example.com", "role": "viewer"},
        headers=auth_header(owner_token),
    ).json()
    token = invitation_token(db, invitation["public_id"])
    invite = InvitationRepository.get_by_token(db, token)
    invite.email = "INVITEE@EXAMPLE.COM"
    db.commit()

    response = client.post(
        f"/api/v1/invitations/accept/{token}",
        headers=auth_header(invitee_token),
    )

    assert response.status_code == 200


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

    organization_public_id = create_organization(
        client,
        owner_token,
    )

    create_user(
        client,
        "expired@example.com",
        "Expired",
    )

    invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": "expired@example.com",
            "role": "viewer",
        },
        headers=auth_header(owner_token),
    ).json()

    token = invitation_token(db, invitation["public_id"])
    invite = InvitationRepository.get_by_token(db, token)

    invite.expires_at = datetime.now(
        timezone.utc
    ) - timedelta(days=1)

    db.commit()

    invitee_token = login(
        client,
        "expired@example.com",
    )

    response = client.post(
        f"/api/v1/invitations/accept/{token}",
        headers=auth_header(invitee_token),
    )

    assert response.status_code == 400


def test_accept_same_invitation_twice(client, db):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    owner_token = login(
        client,
        "owner@example.com",
    )

    organization_public_id = create_organization(
        client,
        owner_token,
    )

    create_user(
        client,
        "member@example.com",
        "Member",
    )

    invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": "member@example.com",
            "role": "viewer",
        },
        headers=auth_header(owner_token),
    ).json()

    token = invitation_token(db, invitation["public_id"])
    member_token = login(
        client,
        "member@example.com",
    )

    client.post(
        f"/api/v1/invitations/accept/{token}",
        headers=auth_header(member_token),
    )

    response = client.post(
        f"/api/v1/invitations/accept/{token}",
        headers=auth_header(member_token),
    )

    assert response.status_code == 400

def test_cancel_invitation(client):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    token = login(
        client,
        "owner@example.com",
    )

    organization_public_id = create_organization(
        client,
        token,
    )

    create_user(
        client,
        "invitee@example.com",
        "Invitee",
    )

    invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": "invitee@example.com",
            "role": "viewer",
        },
        headers=auth_header(token),
    ).json()

    response = client.delete(
        f"/api/v1/invitations/{invitation['public_id']}",
        headers=auth_header(token),
    )

    assert response.status_code == 204

def test_cancel_missing_invitation(client):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    token = login(
        client,
        "owner@example.com",
    )

    response = client.delete(
        "/api/v1/invitations/11111111-1111-1111-1111-111111111111",
        headers=auth_header(token),
    )

    assert response.status_code == 404

def test_resend_invitation(client, db):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    owner_token = login(
        client,
        "owner@example.com",
    )

    organization_public_id = create_organization(
        client,
        owner_token,
    )

    create_user(
        client,
        "invitee@example.com",
        "Invitee",
    )

    invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": "invitee@example.com",
            "role": "viewer",
        },
        headers=auth_header(owner_token),
    ).json()

    old_token = invitation_token(db, invitation["public_id"])
    response = client.post(
        f"/api/v1/invitations/{invitation['public_id']}/resend",
        headers=auth_header(owner_token),
    )

    assert response.status_code == 200
    assert response.json()["public_id"] == invitation['public_id']
    assert "token" not in response.json()
    new_token = invitation_token(db, invitation["public_id"])
    assert new_token != old_token

def test_resend_missing_invitation(client):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    token = login(
        client,
        "owner@example.com",
    )

    response = client.post(
        "/api/v1/invitations/11111111-1111-1111-1111-111111111111/resend",
        headers=auth_header(token),
    )

    assert response.status_code == 404

def test_resend_accepted_invitation(client, db):

    create_user(
        client,
        "owner@example.com",
        "Owner",
    )

    owner_token = login(
        client,
        "owner@example.com",
    )

    organization_public_id = create_organization(
        client,
        owner_token,
    )

    create_user(
        client,
        "member@example.com",
        "Member",
    )

    invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": "member@example.com",
            "role": "viewer",
        },
        headers=auth_header(owner_token),
    ).json()

    token = invitation_token(db, invitation["public_id"])
    member_token = login(
        client,
        "member@example.com",
    )

    client.post(
        f"/api/v1/invitations/accept/{token}",
        headers=auth_header(member_token),
    )

    response = client.post(
        f"/api/v1/invitations/{invitation['public_id']}/resend",
        headers=auth_header(owner_token),
    )

    assert response.status_code == 400


def test_invitation_contract_hides_tokens_and_preserves_link_access(client, db):
    create_user(client, "owner@example.com", "Owner")
    owner_token = login(client, "owner@example.com")
    organization_public_id = create_organization(client, owner_token)

    create_user(client, "invitee@example.com", "Invitee")
    invitation_response = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={"email": "invitee@example.com", "role": "viewer"},
        headers=auth_header(owner_token),
    )
    invitation = invitation_response.json()
    stored_token = invitation_token(db, invitation["public_id"])

    assert invitation_response.status_code == 200
    assert "token" not in invitation

    listed = client.get(
        f"/api/v1/invitations/{organization_public_id}",
        headers=auth_header(owner_token),
    )
    assert listed.status_code == 200
    assert all("token" not in item for item in listed.json())

    invitee_token = login(client, "invitee@example.com")
    notifications = client.get(
        "/api/v1/notifications/",
        headers=auth_header(invitee_token),
    )
    assert notifications.status_code == 200
    assert notifications.json()[0]["reference_id"] == invitation["public_id"]
    assert stored_token not in notifications.text

    legacy_notification = db.query(Notification).first()
    legacy_notification.reference_id = stored_token
    db.commit()
    legacy_notifications = client.get(
        "/api/v1/notifications/",
        headers=auth_header(invitee_token),
    )
    assert legacy_notifications.status_code == 200
    assert legacy_notifications.json()[0]["reference_id"] == invitation["public_id"]
    assert stored_token not in legacy_notifications.text

    owner_link = client.get(
        f"/api/v1/invitations/{invitation['public_id']}/link",
        headers=auth_header(owner_token),
    )
    assert owner_link.status_code == 200
    assert owner_link.json()["acceptance_url"].endswith(
        f"/invitations/accept/{stored_token}"
    )
    assert invitation_token(db, invitation["public_id"]) == stored_token

    resend = client.post(
        f"/api/v1/invitations/{invitation['public_id']}/resend",
        headers=auth_header(owner_token),
    )
    assert resend.status_code == 200
    assert "token" not in resend.json()
    rotated_token = invitation_token(db, invitation["public_id"])
    assert rotated_token != stored_token

    invitee_link = client.get(
        f"/api/v1/invitations/{invitation['public_id']}/link",
        headers=auth_header(invitee_token),
    )
    assert invitee_link.status_code == 200
    assert invitee_link.json()["acceptance_url"].endswith(
        f"/invitations/accept/{rotated_token}"
    )

    accepted = client.post(
        f"/api/v1/invitations/accept/{rotated_token}",
        headers=auth_header(invitee_token),
    )
    assert accepted.status_code == 200


def test_invitation_link_requires_org_admin_or_intended_invitee(client, db):
    create_user(client, "owner@example.com", "Owner")
    owner_token = login(client, "owner@example.com")
    organization_public_id = create_organization(client, owner_token)

    create_user(client, "invitee@example.com", "Invitee")
    invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={"email": "invitee@example.com", "role": "viewer"},
        headers=auth_header(owner_token),
    ).json()
    invitation_id = invitation["public_id"]
    stored_token = invitation_token(db, invitation_id)

    create_user(client, "member@example.com", "Member")
    member_invitation = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={"email": "member@example.com", "role": "viewer"},
        headers=auth_header(owner_token),
    ).json()
    member_token = login(client, "member@example.com")
    member_invitation_token = invitation_token(
        db,
        member_invitation["public_id"],
    )
    assert client.post(
        f"/api/v1/invitations/accept/{member_invitation_token}",
        headers=auth_header(member_token),
    ).status_code == 200

    member_link = client.get(
        f"/api/v1/invitations/{invitation_id}/link",
        headers=auth_header(member_token),
    )
    assert member_link.status_code == 403

    create_user(client, "outsider@example.com", "Outsider")
    outsider_token = login(client, "outsider@example.com")
    outsider_link = client.get(
        f"/api/v1/invitations/{invitation_id}/link",
        headers=auth_header(outsider_token),
    )
    assert outsider_link.status_code == 403
    assert invitation_token(db, invitation_id) == stored_token