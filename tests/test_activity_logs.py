from tests.test_organizations import (
    auth_header,
    get_token,
    create_organization,
)
from app.models.invitation import Invitation
from app.models.organization import Organization
from app.models.task import Task
from app.models.user import User
from app.schemas.activity_log import ActivityLogResponse
from app.services.activity_log_service import ActivityLogService
from app.services.organization_overview_service import OrganizationOverviewService
from uuid import UUID

def test_list_activity_logs(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    response = client.get(
        f"/api/v1/activity-logs/{organization_public_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_activity_logs_invalid_org(client):

    token = get_token(client)

    response = client.get(
        "/api/v1/activity-logs/11111111-1111-1111-1111-111111111111",
        headers=auth_header(token),
    )

    assert response.status_code == 404

def test_activity_logs_requires_login(client):

    response = client.get(
        "/api/v1/activity-logs/11111111-1111-1111-1111-111111111111",
    )

    assert response.status_code == 401

def test_activity_log_created(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Backend",
            "description": "API",
        },
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/activity-logs/{organization_public_id}",
        headers=auth_header(token),
    )

    logs = response.json()

    assert len(logs) >= 2

def test_activity_logs_sorted(client):

    token = get_token(client)

    organization_public_id = create_organization(
        client,
        token,
    )

    client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "First",
            "description": "One",
        },
        headers=auth_header(token),
    )

    client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={
            "name": "Second",
            "description": "Two",
        },
        headers=auth_header(token),
    )

    response = client.get(
        f"/api/v1/activity-logs/{organization_public_id}",
        headers=auth_header(token),
    )

    logs = response.json()

    assert logs[0]["created_at"] >= logs[1]["created_at"]


def test_activity_logs_expose_target_public_uuids(client, db):
    token = get_token(client)
    organization_public_id = create_organization(client, token)

    project_response = client.post(
        f"/api/v1/projects/{organization_public_id}",
        json={"name": "Target Project", "description": "Targets"},
        headers=auth_header(token),
    )
    project_public_id = project_response.json()["public_id"]

    task_response = client.post(
        f"/api/v1/projects/{project_public_id}/tasks",
        json={
            "title": "Target Task",
            "description": "Targets",
            "status": "todo",
            "priority": "medium",
            "assignee_id": None,
            "due_date": None,
        },
        headers=auth_header(token),
    )
    task_public_id = task_response.json()["public_id"]

    comment_response = client.post(
        f"/api/v1/comments/task/{task_public_id}",
        json={"content": "Target Comment"},
        headers=auth_header(token),
    )
    comment_public_id = comment_response.json()["public_id"]

    member_response = client.post(
        f"/api/v1/auth/register",
        json={
            "email": "activity-member@example.com",
            "password": "password123",
            "full_name": "Activity Member",
        },
    )
    member_public_id = member_response.json()["public_id"]
    membership_response = client.post(
        f"/api/v1/organizations/{organization_public_id}/members",
        json={"user_id": member_public_id, "role": "viewer"},
        headers=auth_header(token),
    )
    membership_public_id = membership_response.json()["public_id"]

    invitee_response = client.post(
        f"/api/v1/auth/register",
        json={
            "email": "activity-invitee@example.com",
            "password": "password123",
            "full_name": "Activity Invitee",
        },
    )
    invitation_response = client.post(
        f"/api/v1/invitations/{organization_public_id}/invite",
        json={
            "email": invitee_response.json()["email"],
            "role": "viewer",
        },
        headers=auth_header(token),
    )
    invitation_public_id = invitation_response.json()["public_id"]

    organization = db.query(Organization).filter(
        Organization.public_id == organization_public_id,
    ).one()
    owner = db.query(User).filter(User.email == "owner@example.com").one()
    task = db.query(Task).filter(Task.public_id == task_public_id).one()
    ActivityLogService.log(
        db=db,
        organization_id=organization.id,
        user_id=owner.id,
        action="task_reviewed",
        target_type="task",
        target_id=task.id,
        description="Reviewed target task",
    )
    invitation = db.query(Invitation).filter(
        Invitation.public_id == invitation_public_id,
    ).one()
    ActivityLogService.log(
        db=db,
        organization_id=organization.id,
        user_id=owner.id,
        action="invitation_reviewed",
        target_type="invitation",
        target_id=invitation.id,
        description="Reviewed target invitation",
    )

    response = client.get(
        f"/api/v1/activity-logs/{organization_public_id}",
        headers=auth_header(token),
    )
    assert response.status_code == 200
    logs = response.json()
    targets = {
        log["target_type"]: log["target_public_id"]
        for log in logs
        if log["target_type"] in {
            "organization",
            "project",
            "task",
            "comment",
            "membership",
            "invitation",
        }
    }

    assert all("target_id" not in log for log in logs)
    assert targets["organization"] == organization_public_id
    assert targets["project"] == project_public_id
    assert targets["task"] == task_public_id
    assert targets["comment"] == comment_public_id
    assert targets["membership"] == membership_public_id
    assert targets["invitation"] == invitation_public_id

    overview = OrganizationOverviewService.get_overview(
        db,
        UUID(organization_public_id),
        owner,
    )
    overview_logs = [
        ActivityLogResponse.model_validate(
            log,
            from_attributes=True,
        ).model_dump()
        for log in overview["recent_activity"]
    ]
    assert all(
        "target_id" not in log
        for log in overview_logs
    )