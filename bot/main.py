import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.handlers import register_dependencies, router
from bot.services.calculator import CalculatorService
from bot.services.car_catalog import CarCatalog
from bot.services.google_sheets import GoogleSheetsClient
from bot.services.history import HistoryService


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    sheets = GoogleSheetsClient()
    catalog = CarCatalog()
    catalog.load(sheets.get_car_rows())

    calculator = CalculatorService(sheets)
    history = HistoryService(sheets)
    register_dependencies(catalog, calculator, history, bot)

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
