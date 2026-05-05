from __future__ import annotations

from bot.services.google_sheets import GoogleSheetsClient


class CalculatorService:
    def __init__(self, sheets: GoogleSheetsClient) -> None:
        self.sheets = sheets

    def calculate(self, brand: str, model: str, year: str, engine: str, invoice: str, real_price_krw: str) -> list[list[str]]:
        self.sheets.write_calc_inputs(
            brand=brand,
            model=model,
            year=year,
            engine=engine,
            invoice=invoice,
            real_price_krw=real_price_krw,
        )
        return self.sheets.read_calc_snapshot()
