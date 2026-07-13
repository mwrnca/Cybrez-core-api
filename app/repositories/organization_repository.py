from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:

    @staticmethod
    def create(db: Session, organization: Organization):
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization

    @staticmethod
    def get_by_id(db: Session, organization_id: int):
        return (
            db.query(Organization)
            .filter(Organization.id == organization_id)
            .first()
        )

    @staticmethod
    def get_by_slug(db: Session, slug: str):
        return (
            db.query(Organization)
            .filter(Organization.slug == slug)
            .first()
        )

    @staticmethod
    def get_all(db: Session):
        return db.query(Organization).all()

    @staticmethod
    def update(db: Session, organization: Organization):
        db.commit()
        db.refresh(organization)
        return organization

    @staticmethod
    def delete(db: Session, organization: Organization):
        db.delete(organization)
        db.commit()

 