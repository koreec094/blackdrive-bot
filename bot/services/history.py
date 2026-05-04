from __future__ import annotations

from bot.services.google_sheets import GoogleSheetsClient


class HistoryService:
    def __init__(self, sheets: GoogleSheetsClient) -> None:
        self.sheets = sheets

    def save_success(self, telegram_id: int, username: str, brand: str, model: str, year: str, engine: str, price_usd: str, total: str, currency: str) -> None:
        self.sheets.append_history([
            self.sheets.now_str(), str(telegram_id), username or '', brand, model, year, engine, price_usd, total, currency,
        ])

    def save_request(self, telegram_id: int, username: str, full_name: str, brand: str, model: str, year: str, engine: str, comment: str) -> None:
        self.sheets.append_request([
            self.sheets.now_str(), str(telegram_id), username or '', full_name or '', brand, model, year, engine, comment, 'new',
        ])
