from app.schemas.common import APIModel


class CsvImportIssue(APIModel):
    row_number: int
    code: str
    message: str


class CsvImportSummary(APIModel):
    total_rows: int
    inserted: int
    duplicates_skipped: int
    invalid_rows: int
    dry_run: bool


class CsvImportResponse(APIModel):
    summary: CsvImportSummary
    errors: list[CsvImportIssue]
    warnings: list[CsvImportIssue]
