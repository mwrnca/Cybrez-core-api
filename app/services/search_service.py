from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.search_repository import SearchRepository


class SearchService:

    @staticmethod
    def search(
        db: Session,
        query: str,
        current_user: User,
    ):
        results = []

        organizations = SearchRepository.search_organizations(db, query)
        projects = SearchRepository.search_projects(db, query)
        tasks = SearchRepository.search_tasks(db, query)
        comments = SearchRepository.search_comments(db, query)
        members = SearchRepository.search_members(db, query)

        results.extend(
            {
                "type": "Organization",
                "public_id": str(o.public_id),
                "title": o.name,
                "subtitle": o.description or "",
                "url": f"/organizations/{o.public_id}",
            }
            for o in organizations
        )

        results.extend(
            {
                "type": "Project",
                "public_id": str(p.public_id),
                "title": p.name,
                "subtitle": p.description or "",
                "url": f"/projects/{p.public_id}",
            }
            for p in projects
        )

        results.extend(
            {
                "type": "Task",
                "public_id": str(t.public_id),
                "title": t.title,
                "subtitle": str(t.status),
                "url": f"/tasks/{t.public_id}",
            }
            for t in tasks
        )

        results.extend(
            {
                "type": "Comment",
                "public_id": str(c.public_id),
                "title": c.content[:50],
                "subtitle": "Comment",
                "url": f"/comments/{c.public_id}",
            }
            for c in comments
        )

        results.extend(
            {
                "type": "Member",
                "public_id": str(m.public_id),
                "title": m.name,
                "subtitle": m.email,
                "url": f"/users/{m.public_id}",
            }
            for m in members
        )

        return results