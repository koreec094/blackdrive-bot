from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    bot_token: str = Field(alias='BOT_TOKEN')
    google_sheet_id: str = Field(alias='GOOGLE_SHEET_ID')
    google_service_account_json: str = Field(alias='GOOGLE_SERVICE_ACCOUNT_JSON')
    admin_ids_raw: str = Field(default='', alias='ADMIN_IDS')

    main_channel_id: str = Field(default='', alias='MAIN_CHANNEL_ID')
    main_channel_url: str = Field(default='https://t.me/blackdriveauto', alias='MAIN_CHANNEL_URL')
    manager_telegram: str = Field(default='@blackdriveauto1', alias='MANAGER_TELEGRAM')
    manager_whatsapp: str = Field(default='wa.me/77085217861', alias='MANAGER_WHATSAPP')

    calc_sheet_name: str = Field(default='Казахстан/Алматы', alias='CALC_SHEET_NAME')
    car_db_sheet_name: str = Field(default='База авто', alias='CAR_DB_SHEET_NAME')
    requests_sheet_name: str = Field(default='Заявки', alias='REQUESTS_SHEET_NAME')
    history_sheet_name: str = Field(default='История расчетов', alias='HISTORY_SHEET_NAME')

    calc_input_brand_cell: str = Field(default='B3', alias='CALC_INPUT_BRAND_CELL')
    calc_input_model_cell: str = Field(default='B4', alias='CALC_INPUT_MODEL_CELL')
    calc_input_year_cell: str = Field(default='B5', alias='CALC_INPUT_YEAR_CELL')
    calc_input_engine_cell: str = Field(default='B6', alias='CALC_INPUT_ENGINE_CELL')
    calc_input_invoice_cell: str = Field(default='B8', alias='CALC_INPUT_INVOICE_CELL')
    calc_input_real_price_cell: str = Field(default='B11', alias='CALC_INPUT_REAL_PRICE_CELL')

    car_to_almaty_total_cell: str = Field(default='', alias='CAR_TO_ALMATY_TOTAL_CELL')
    customs_total_cell: str = Field(default='', alias='CUSTOMS_TOTAL_CELL')
    final_total_cell: str = Field(default='', alias='FINAL_TOTAL_CELL')

    calc_output_range: str = Field(default='A1:Z60', alias='CALC_OUTPUT_RANGE')
    cache_ttl_minutes: int = Field(default=20, alias='CACHE_TTL_MINUTES')

    @property
    def admin_ids(self) -> set[int]:
        return {int(x.strip()) for x in self.admin_ids_raw.split(',') if x.strip()}


settings = Settings()
