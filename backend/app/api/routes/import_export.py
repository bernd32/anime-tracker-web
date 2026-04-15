from datetime import date

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile

from app.api.deps import get_import_export_service, require_owner_write_access
from app.schemas.import_export import CsvImportResponse
from app.services.import_export import ImportExportService

router = APIRouter()


@router.post("/import/csv", response_model=CsvImportResponse)
async def import_csv(
    file: UploadFile = File(...),
    dry_run: bool = Query(default=False),
    service: ImportExportService = Depends(get_import_export_service),
    _: None = Depends(require_owner_write_access),
) -> CsvImportResponse:
    content = await file.read()
    return service.import_csv(content, dry_run=dry_run)


@router.get("/export/csv")
def export_csv(service: ImportExportService = Depends(get_import_export_service)) -> Response:
    content = service.export_csv()
    filename = f"anime_backlog_{date.today().isoformat()}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
