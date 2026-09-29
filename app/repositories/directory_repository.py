from uuid import UUID

from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User


class DirectoryRepository:

    @staticmethod
    def get_people(
        db: Session,
    ):
        rows = (
            db.query(User, Membership, Organization)
            .join(
                Membership,
                Membership.user_id == User.public_id,
            )
            .join(
                Organization,
                Organization.public_id == Membership.organization_id,
            )
            .filter(
                User.is_active.is_(True),
                User.deleted_at.is_(None),
                Organization.deleted_at.is_(None),
            )
            .order_by(
                User.full_name.asc(),
                Organization.name.asc(),
            )
            .all()
        )

        people: dict[UUID, dict] = {}

        for user, membership, organization in rows:
            if user.public_id not in people:
                people[user.public_id] = {
                    "public_id": user.public_id,
                    "full_name": user.full_name,
                    "organizations": [],
                }

            people[user.public_id]["organizations"].append(
                {
                    "public_id": organization.public_id,
                    "name": organization.name,
                    "description": organization.description,
                    "logo_url": organization.logo_url,
                    "role": membership.role,
                }
            )

        return list(people.values())