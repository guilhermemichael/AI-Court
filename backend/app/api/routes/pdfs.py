import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories import CaseRepository, VerdictRepository
from app.infrastructure.db.session import get_session
from app.infrastructure.pdf.verdict_pdf import VerdictPdfRenderer
from app.settings import get_settings

router = APIRouter(prefix="/pdfs", tags=["pdfs"])
settings = get_settings()


@router.get("/{case_id}")
async def download_pdf(
    case_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> FileResponse:
    case = await CaseRepository(session).get(case_id)
    verdict = await VerdictRepository(session).get_by_case(case_id)
    if case is None or verdict is None:
        raise HTTPException(status_code=404, detail="verdict_not_found")
    path = VerdictPdfRenderer(Path(settings.pdf_storage_path), settings.pdf_base_url).render(
        case, verdict
    )
    return FileResponse(
        path, media_type="application/pdf", filename=f"ai-court-verdict-{case_id}.pdf"
    )
