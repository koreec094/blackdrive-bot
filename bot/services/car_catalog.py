from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from bot.config import settings
from bot.utils.normalize import normalize_engine, normalize_text


@dataclass
class CarRecord:
    brand: str
    model: str
    engine: str
    year: str
    price_usd: str


class CarCatalog:
    def __init__(self) -> None:
        self.records: list[CarRecord] = []
        self.updated_at: datetime | None = None

    def load(self, rows: list[list[str]]) -> None:
        self.records = [
            CarRecord(
                brand=(r[1] if len(r) > 1 else '').strip(),
                model=(r[2] if len(r) > 2 else '').strip(),
                engine=(r[3] if len(r) > 3 else '').strip(),
                year=(r[4] if len(r) > 4 else '').strip(),
                price_usd=(r[5] if len(r) > 5 else '').strip(),
            )
            for r in rows
            if len(r) >= 6
        ]
        self.updated_at = datetime.utcnow()

    def is_stale(self) -> bool:
        if not self.updated_at:
            return True
        return datetime.utcnow() - self.updated_at > timedelta(minutes=settings.cache_ttl_minutes)

    def brands(self) -> list[str]:
        return sorted({r.brand for r in self.records})

    def models(self, brand: str) -> list[str]:
        nb = normalize_text(brand)
        return sorted({r.model for r in self.records if normalize_text(r.brand) == nb})

    def years(self, brand: str, model: str) -> list[str]:
        nb, nm = normalize_text(brand), normalize_text(model)
        return sorted({r.year for r in self.records if normalize_text(r.brand) == nb and normalize_text(r.model) == nm})

    def engines(self, brand: str, model: str, year: str) -> list[str]:
        nb, nm, ny = normalize_text(brand), normalize_text(model), normalize_text(year)
        return sorted({r.engine for r in self.records if normalize_text(r.brand) == nb and normalize_text(r.model) == nm and normalize_text(r.year) == ny})

    def find(self, brand: str, model: str, year: str, engine: str) -> CarRecord | None:
        nb, nm, ny, ne = normalize_text(brand), normalize_text(model), normalize_text(year), normalize_engine(engine)
        for r in self.records:
            if normalize_text(r.brand) == nb and normalize_text(r.model) == nm and normalize_text(r.year) == ny and normalize_engine(r.engine) == ne:
                return r
        return None
