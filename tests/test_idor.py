"""
Cross-organization access control tests (IDOR).

For every resource type, User B (member/owner of Organization B) must
never be able to read, modify, or delete a resource that belongs to
Organization A, even when they know its UUID. Expected result is
always 403 or 404 -- never 200.
"""

from tests.test_organizations import organization_payload


def create_user(client, email, name="Test User"):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": name,
        },
    )
    assert response.status_code == 201
    return response.json()


def login(client, email):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def create_org(client, token, name="Org", slug="org"):
    response = client.post(
        "/api/v1/organizations",
        json=organization_payload(name=name, slug=slug),
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.json()["public_id"]


def create_project(client, token, organization_public_id):
    response = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={"name": "Backend", "description": "API"},
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.json()["public_id"]


def create_task(client, token, project_public_id):
    response = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json={
            "title": "Implement API",
            "description": "Write backend",
            "status": "todo",
            "priority": "medium",
            "assignee_id": None,
            "due_date": None,
        },
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.json()["public_id"]


def create_comment(client, token, task_public_id):
    response = client.post(
        f"/api/v1/comments/task/{task_public_id}",
        json={"content": "First comment"},
        headers=auth_header(token),
    )
    assert response.status_code == 201
    return response.json()["public_id"]


def two_orgs_with_full_resources(client):
    """
    Sets up:
      User A -> Organization A -> Project A -> Task A -> Comment A
      User B -> Organization B (unrelated)

    Returns a dict of everything the tests need.
    """
    owner_a = create_user(client, "owner-a@example.com", "Owner A")
    token_a = login(client, "owner-a@example.com")
    org_a = create_org(client, token_a, name="Org A", slug="org-a")
    project_a = create_project(client, token_a, org_a)
    task_a = create_task(client, token_a, project_a)
    comment_a = create_comment(client, token_a, task_a)

    invitation_a = client.post(
        f"/api/v1/invitations/{org_a}/invite",
        json={"email": "someone@example.com", "role": "viewer"},
        headers=auth_header(token_a),
    ).json()

    owner_b = create_user(client, "owner-b@example.com", "Owner B")
    token_b = login(client, "owner-b@example.com")
    org_b = create_org(client, token_b, name="Org B", slug="org-b")

    return {
        "token_a": token_a,
        "owner_a_public_id": owner_a["public_id"],
        "org_a": org_a,
        "project_a": project_a,
        "task_a": task_a,
        "comment_a": comment_a,
        "invitation_a": invitation_a,
        "token_b": token_b,
        "owner_b_public_id": owner_b["public_id"],
        "org_b": org_b,
    }


# ---------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------

def test_cannot_view_other_org(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.get(
        f"/api/v1/organizations/{ctx['org_a']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_update_other_org(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.put(
        f"/api/v1/organizations/{ctx['org_a']}",
        json=organization_payload(name="Hijacked", slug="hijacked"),
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_delete_other_org(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.delete(
        f"/api/v1/organizations/{ctx['org_a']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


# ---------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------

def test_cannot_list_other_org_projects(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.get(
        f"/api/v1/projects/organization/{ctx['org_a']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_view_other_org_project(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.get(
        f"/api/v1/projects/{ctx['project_a']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_update_other_org_project(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.put(
        f"/api/v1/projects/{ctx['project_a']}",
        json={"name": "Hijacked", "description": "Hijacked"},
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_delete_other_org_project(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.delete(
        f"/api/v1/projects/{ctx['project_a']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_archive_other_org_project(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.post(
        f"/api/v1/projects/{ctx['project_a']}/archive",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_restore_other_org_project(client):
    ctx = two_orgs_with_full_resources(client)

    client.delete(
        f"/api/v1/projects/{ctx['project_a']}",
        headers=auth_header(ctx["token_a"]),
    )

    response = client.post(
        f"/api/v1/projects/{ctx['project_a']}/restore",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


# ---------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------

def test_cannot_list_other_org_tasks(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.get(
        f"/api/v1/projects/{ctx['project_a']}/tasks",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_create_task_in_other_org_project(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.post(
        f"/api/v1/projects/{ctx['project_a']}/tasks",
        json={
            "title": "Injected",
            "description": "Injected",
            "status": "todo",
            "priority": "medium",
            "assignee_id": None,
            "due_date": None,
        },
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_update_other_org_task(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.put(
        f"/api/v1/projects/tasks/{ctx['task_a']}",
        json={
            "title": "Hijacked",
            "description": "Hijacked",
            "status": "in_progress",
            "priority": "high",
            "assignee_id": None,
            "due_date": None,
        },
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_delete_other_org_task(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.delete(
        f"/api/v1/projects/{ctx['project_a']}/tasks/{ctx['task_a']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_archive_other_org_task(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.post(
        f"/api/v1/projects/tasks/{ctx['task_a']}/archive",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


# ---------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------

def test_cannot_list_other_org_comments(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.get(
        f"/api/v1/comments/task/{ctx['task_a']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_create_comment_on_other_org_task(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.post(
        f"/api/v1/comments/task/{ctx['task_a']}",
        json={"content": "Injected comment"},
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_update_other_org_comment(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.put(
        f"/api/v1/comments/{ctx['comment_a']}",
        json={"content": "Hijacked"},
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_delete_other_org_comment(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.delete(
        f"/api/v1/comments/{ctx['comment_a']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


# ---------------------------------------------------------------------
# Activity logs
# ---------------------------------------------------------------------

def test_cannot_view_other_org_activity_logs(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.get(
        f"/api/v1/activity-logs/{ctx['org_a']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


# ---------------------------------------------------------------------
# Memberships
# ---------------------------------------------------------------------

def test_cannot_list_other_org_members(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.get(
        f"/api/v1/organizations/{ctx['org_a']}/members",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_add_member_to_other_org(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.post(
        f"/api/v1/organizations/{ctx['org_a']}/members",
        json={"user_id": ctx["owner_b_public_id"], "role": "viewer"},
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_remove_other_org_member(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.delete(
        f"/api/v1/organizations/{ctx['org_a']}/members/{ctx['owner_a_public_id']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


# ---------------------------------------------------------------------
# Invitations
# ---------------------------------------------------------------------

def test_cannot_invite_to_other_org(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.post(
        f"/api/v1/invitations/{ctx['org_a']}/invite",
        json={"email": "injected@example.com", "role": "viewer"},
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_cancel_other_org_invitation(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.delete(
        f"/api/v1/invitations/{ctx['invitation_a']['public_id']}",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)


def test_cannot_resend_other_org_invitation(client):
    ctx = two_orgs_with_full_resources(client)

    response = client.post(
        f"/api/v1/invitations/{ctx['invitation_a']['public_id']}/resend",
        headers=auth_header(ctx["token_b"]),
    )

    assert response.status_code in (403, 404)