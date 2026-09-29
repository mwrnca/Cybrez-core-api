from uuid import UUID

from sqlalchemy.orm import Session

from app.models.organization_unit import OrganizationUnit


class OrganizationUnitRepository:

    @staticmethod
    def get_by_public_id(
        db: Session,
        public_id: UUID,
    ) -> OrganizationUnit | None:
        return (
            db.query(OrganizationUnit)
            .filter(
                OrganizationUnit.public_id == public_id,
                OrganizationUnit.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        unit_id: int,
    ) -> OrganizationUnit | None:
        return (
            db.query(OrganizationUnit)
            .filter(
                OrganizationUnit.id == unit_id,
                OrganizationUnit.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_for_organization(
        db: Session,
        organization_id: UUID,
    ) -> list[OrganizationUnit]:
        return (
            db.query(OrganizationUnit)
            .filter(
                OrganizationUnit.organization_id == organization_id,
                OrganizationUnit.deleted_at.is_(None),
            )
            .order_by(
                OrganizationUnit.name.asc(),
            )
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        organization_id: UUID,
        name: str,
        description: str | None = None,
        parent_unit_id: int | None = None,
    ) -> OrganizationUnit:
        unit = OrganizationUnit(
            organization_id=organization_id,
            name=name,
            description=description,
            parent_unit_id=parent_unit_id,
        )

        db.add(unit)
        db.commit()
        db.refresh(unit)

        return unit

    @staticmethod
    def update(
        db: Session,
        unit: OrganizationUnit,
        **values,
    ) -> OrganizationUnit:
        for key, value in values.items():
            if value is not None:
                setattr(unit, key, value)

        db.commit()
        db.refresh(unit)

        return unit

    @staticmethod
    def delete(
        db: Session,
        unit: OrganizationUnit,
    ) -> None:
        unit.deleted_at = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        )

        db.commit()