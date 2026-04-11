from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import YearScaffold


class YearScaffoldRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, year: int) -> YearScaffold | None:
        return self.session.get(YearScaffold, year)

    def list_years(self) -> list[int]:
        stmt = select(YearScaffold.year).order_by(YearScaffold.year.desc())
        return [int(row[0]) for row in self.session.execute(stmt).all()]

    def create(self, year: int) -> YearScaffold:
        scaffold = YearScaffold(year=year)
        self.session.add(scaffold)
        self.session.flush()
        self.session.refresh(scaffold)
        return scaffold

    def delete(self, year: int) -> bool:
        scaffold = self.get(year)
        if scaffold is None:
            return False
        self.session.delete(scaffold)
        self.session.flush()
        return True
