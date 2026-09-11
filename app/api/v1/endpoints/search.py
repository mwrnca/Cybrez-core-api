from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.search_service import SearchService
from app.core.rate_limit import search_limiter, user_rate_limit

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get(
    "/",
    dependencies=[Depends(user_rate_limit(search_limiter))],
)
def search(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SearchService.search(
        db=db,
        query=q,
        current_user=current_user,
    )