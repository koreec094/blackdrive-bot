from __future__ import annotations

from datetime import datetime

import gspread
from gspread.worksheet import Worksheet

from bot.config import settings


class GoogleSheetsClient:
    def __init__(self) -> None:
        gc = gspread.service_account(filename=settings.google_service_account_json)
        self.spreadsheet = gc.open_by_key(settings.google_sheet_id)

    def ws(self, title: str) -> Worksheet:
        return self.spreadsheet.worksheet(title)

    def get_car_rows(self) -> list[list[str]]:
        return self.ws(settings.car_db_sheet_name).get_all_values()[1:]

    def append_request(self, values: list[str]) -> None:
        self.ws(settings.requests_sheet_name).append_row(values, value_input_option='USER_ENTERED')

    def append_history(self, values: list[str]) -> None:
        self.ws(settings.history_sheet_name).append_row(values, value_input_option='USER_ENTERED')

    def write_calc_inputs(self, brand: str, model: str, year: str, engine: str, invoice: str) -> None:
        ws = self.ws(settings.calc_sheet_name)
        ws.update_acell(settings.calc_input_brand_cell, brand)
        ws.update_acell(settings.calc_input_model_cell, model)
        ws.update_acell(settings.calc_input_year_cell, year)
        ws.update_acell(settings.calc_input_engine_cell, engine)
        ws.update_acell(settings.calc_input_invoice_cell, invoice)

    def read_calc_snapshot(self) -> list[list[str]]:
        return self.ws(settings.calc_sheet_name).get(settings.calc_output_range)

    @staticmethod
    def now_str() -> str:
        return datetime.utcnow().isoformat(timespec='seconds')
