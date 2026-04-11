from dataclasses import dataclass


@dataclass(slots=True)
class ParsedCsvRow:
    name: str
    year: str
    season: str
    status: str
    type: str
    comment: str
    url: str
    downloaded: str


CANONICAL_HEADER = ["id", "name", "year", "season", "status", "type", "comment", "url", "downloaded"]


HEADER_SET = {value.casefold() for value in CANONICAL_HEADER}


def looks_like_header(row: list[str]) -> bool:
    lowered = {value.strip().casefold() for value in row}
    return bool(lowered & HEADER_SET)


def parse_csv_row(row: list[str]) -> ParsedCsvRow:
    if len(row) == 7:
        name, year, season, status, type_, comment, url = row
        downloaded = "0"
    elif len(row) == 8:
        if row[0].strip().isdigit():
            _, name, year, season, status, type_, comment, url = row
            downloaded = "0"
        else:
            name, year, season, status, type_, comment, url, downloaded = row
    elif len(row) == 9:
        _, name, year, season, status, type_, comment, url, downloaded = row
    else:
        raise ValueError(f"Unsupported CSV row length: {len(row)}")
    return ParsedCsvRow(
        name=name,
        year=year,
        season=season,
        status=status,
        type=type_,
        comment=comment,
        url=url,
        downloaded=downloaded,
    )
