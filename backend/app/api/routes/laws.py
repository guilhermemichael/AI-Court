from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories import HouseLawRepository
from app.infrastructure.db.session import get_session

router = APIRouter(prefix="/laws", tags=["laws"])


@router.get("")
async def list_laws(
    session: AsyncSession = Depends(get_session),
) -> dict[str, list[dict[str, object]]]:
    laws = await HouseLawRepository(session).list_all(limit=12)
    return {
        "items": [
            {
                "id": law.id,
                "title": law.title,
                "article_number": law.article_number,
                "description": law.description,
                "severity": law.severity,
            }
            for law in laws
        ]
    }
