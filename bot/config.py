from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    bot_token: str = Field(alias='BOT_TOKEN')
    google_sheet_id: str = Field(alias='GOOGLE_SHEET_ID')
    google_service_account_json: str = Field(alias='GOOGLE_SERVICE_ACCOUNT_JSON')
    admin_ids_raw: str = Field(default='', alias='ADMIN_IDS')

    calc_sheet_name: str = Field(default='Казахстан/Алматы', alias='CALC_SHEET_NAME')
    car_db_sheet_name: str = Field(default='База авто', alias='CAR_DB_SHEET_NAME')
    requests_sheet_name: str = Field(default='Заявки', alias='REQUESTS_SHEET_NAME')
    history_sheet_name: str = Field(default='История расчетов', alias='HISTORY_SHEET_NAME')

    calc_input_brand_cell: str = Field(default='B3', alias='CALC_INPUT_BRAND_CELL')
    calc_input_model_cell: str = Field(default='B4', alias='CALC_INPUT_MODEL_CELL')
    calc_input_year_cell: str = Field(default='B5', alias='CALC_INPUT_YEAR_CELL')
    calc_input_engine_cell: str = Field(default='B6', alias='CALC_INPUT_ENGINE_CELL')
    calc_input_invoice_cell: str = Field(default='B8', alias='CALC_INPUT_INVOICE_CELL')
    calc_output_range: str = Field(default='A1:Z60', alias='CALC_OUTPUT_RANGE')
    cache_ttl_minutes: int = Field(default=20, alias='CACHE_TTL_MINUTES')

    @property
    def admin_ids(self) -> set[int]:
        return {int(x.strip()) for x in self.admin_ids_raw.split(',') if x.strip()}


settings = Settings()
