from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.directory_repository import DirectoryRepository
from app.schemas.directory import DirectoryPerson


router = APIRouter(
    prefix="/directory",
    tags=["Directory"],
)


@router.get(
    "",
    response_model=list[DirectoryPerson],
)
def get_directory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DirectoryRepository.get_people(db)