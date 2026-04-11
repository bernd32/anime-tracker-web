from __future__ import annotations

import csv
import io
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from typing import Callable

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.db.models import Anime, AnimeStatus
from app.repositories.anime import AnimeRepository
from app.schemas.import_export import CsvImportIssue, CsvImportResponse, CsvImportSummary
from app.utils.csv_helpers import CANONICAL_HEADER, looks_like_header, parse_csv_row
from app.utils.normalization import normalize_comment, normalize_name, normalize_season, normalize_text
from app.utils.urls import validate_optional_url


_TRUE_VALUES = {"1", "true", "yes", "y", "on"}
_ALLOWED_STATUS_VALUES = {value.value for value in AnimeStatus}
_ALLOWED_SEASON_VALUES = {"", "other", "winter", "spring", "summer", "fall", "autumn"}


@dataclass(slots=True)
class ImportAccumulator:
    total_rows: int = 0
    inserted: int = 0
    duplicates_skipped: int = 0
    invalid_rows: int = 0
    errors: list[CsvImportIssue] = field(default_factory=list)
    warnings: list[CsvImportIssue] = field(default_factory=list)


class ImportExportService:
    def __init__(self, session_factory: Callable[[], AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def import_csv(self, content: bytes, *, dry_run: bool = False) -> CsvImportResponse:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValidationAppError(message="CSV file must be valid UTF-8.") from exc
        if not text.strip():
            raise ValidationAppError(message="CSV file is empty.")
        reader = csv.reader(io.StringIO(text))
        acc = ImportAccumulator()
        seen_in_file: set[tuple[str, int, str]] = set()
        with self.session_factory() as session:
            repo = AnimeRepository(session)
            first = True
            for idx, row in enumerate(reader, start=1):
                if not row or all(not cell.strip() for cell in row):
                    continue
                if first and looks_like_header(row):
                    first = False
                    continue
                first = False
                acc.total_rows += 1
                try:
                    parsed = parse_csv_row(row)
                    year = int(parsed.year)
                    if year < 1960 or year > 2100:
                        raise ValueError("Year must be an integer between 1960 and 2100.")
                    normalized_name = normalize_name(parsed.name)
                    if not normalized_name:
                        raise ValueError("Anime name cannot be empty.")
                    season_raw = (parsed.season or "").strip().lower()
                    season = normalize_season(parsed.season, year)
                    if year >= 2010 and season_raw not in _ALLOWED_SEASON_VALUES:
                        acc.warnings.append(
                            CsvImportIssue(
                                row_number=idx,
                                code="season_coerced",
                                message="Season was coerced to 'other' because the input value was not recognized.",
                            )
                        )
                    if year < 2010 and (parsed.season or "").strip().lower() not in {"", "other"}:
                        acc.warnings.append(
                            CsvImportIssue(
                                row_number=idx,
                                code="season_coerced",
                                message="Season was coerced to 'other' for pre-2010 entry.",
                            )
                        )
                    status_raw = (parsed.status or "unwatched").strip().lower()
                    if status_raw not in _ALLOWED_STATUS_VALUES:
                        acc.warnings.append(
                            CsvImportIssue(
                                row_number=idx,
                                code="status_coerced",
                                message="Status was coerced to 'unwatched' because the input value was not recognized.",
                            )
                        )
                        status = AnimeStatus.UNWATCHED
                    else:
                        status = AnimeStatus(status_raw)
                    downloaded = (parsed.downloaded or "").strip().lower() in _TRUE_VALUES
                    url = validate_optional_url(parsed.url or "")
                    identity = (normalized_name, year, season.value)
                    if identity in seen_in_file:
                        acc.duplicates_skipped += 1
                        continue
                    seen_in_file.add(identity)
                    if repo.exists_by_identity(name_normalized=normalized_name, year=year, season=season):
                        acc.duplicates_skipped += 1
                        continue
                    anime = Anime(
                        name=normalize_text(parsed.name),
                        name_normalized=normalized_name,
                        year=year,
                        season=season,
                        status=status,
                        type=normalize_text(parsed.type),
                        comment=normalize_comment(parsed.comment),
                        url=url,
                        downloaded=downloaded,
                    )
                    if not dry_run:
                        repo.add(anime)
                    acc.inserted += 1
                except Exception as exc:
                    acc.invalid_rows += 1
                    acc.errors.append(
                        CsvImportIssue(row_number=idx, code="csv_row_invalid", message=str(exc))
                    )
            if dry_run:
                session.rollback()
            else:
                session.commit()
        return CsvImportResponse(
            summary=CsvImportSummary(
                total_rows=acc.total_rows,
                inserted=acc.inserted,
                duplicates_skipped=acc.duplicates_skipped,
                invalid_rows=acc.invalid_rows,
                dry_run=dry_run,
            ),
            errors=acc.errors,
            warnings=acc.warnings,
        )

    def export_csv(self) -> str:
        with self.session_factory() as session:
            items = AnimeRepository(session).list(
                scope_kind="all",
                scope_year=None,
                season=None,
                search_normalized=None,
                status=None,
                downloaded=None,
            )
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(CANONICAL_HEADER)
            for anime in items:
                writer.writerow(
                    [
                        anime.id,
                        anime.name,
                        anime.year,
                        anime.season.value,
                        anime.status.value,
                        anime.type,
                        anime.comment,
                        anime.url,
                        int(anime.downloaded),
                    ]
                )
            return output.getvalue()
