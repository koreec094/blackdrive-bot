from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import settings
from bot.keyboards import options_keyboard
from bot.states import CalcStates


router = Router()


def register_dependencies(catalog, calculator, history, bot):
    router.catalog = catalog
    router.calculator = calculator
    router.history = history
    router.bot = bot


@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(CalcStates.choosing_country)
    await message.answer('Выберите страну расчета:', reply_markup=options_keyboard(['Казахстан']))


@router.message(CalcStates.choosing_country, F.text == 'Казахстан')
async def choose_country(message: Message, state: FSMContext):
    await state.set_state(CalcStates.choosing_brand)
    await message.answer('Выберите марку:', reply_markup=options_keyboard(router.catalog.brands()))


@router.message(CalcStates.choosing_brand)
async def choose_brand(message: Message, state: FSMContext):
    brand = message.text.strip()
    await state.update_data(brand=brand, model=None, year=None, engine=None)
    await state.set_state(CalcStates.choosing_model)
    await message.answer('Выберите модель:', reply_markup=options_keyboard(router.catalog.models(brand)))


@router.message(CalcStates.choosing_model)
async def choose_model(message: Message, state: FSMContext):
    data = await state.get_data()
    model = message.text.strip()
    await state.update_data(model=model, year=None, engine=None)
    await state.set_state(CalcStates.choosing_year)
    await message.answer('Выберите год:', reply_markup=options_keyboard(router.catalog.years(data['brand'], model)))


@router.message(CalcStates.choosing_year)
async def choose_year(message: Message, state: FSMContext):
    data = await state.get_data()
    year = message.text.strip()
    await state.update_data(year=year, engine=None)
    await state.set_state(CalcStates.choosing_engine)
    await message.answer('Выберите объем двигателя:', reply_markup=options_keyboard(router.catalog.engines(data['brand'], data['model'], year)))


@router.message(CalcStates.choosing_engine)
async def choose_engine(message: Message, state: FSMContext):
    engine = message.text.strip()
    data = await state.get_data()
    rec = router.catalog.find(data['brand'], data['model'], data['year'], engine)
    if not rec:
        await state.update_data(engine=engine)
        await state.set_state(CalcStates.manual_name)
        await message.answer('По выбранному автомобилю пока нет данных. Введите ваше имя:')
        return

    snapshot = router.calculator.calculate(data['brand'], data['model'], data['year'], engine, rec.price_usd)
    total_line = next((row for row in snapshot if row and 'итог' in row[0].strip().lower()), None)
    total = total_line[1] if total_line and len(total_line) > 1 else '—'
    currency = total_line[2] if total_line and len(total_line) > 2 else '₸/$'

    router.history.save_success(message.from_user.id, message.from_user.username or '', data['brand'], data['model'], data['year'], engine, rec.price_usd, total, currency)
    await message.answer(
        f'Расчет автомобиля для Казахстана\n\nМарка: {data["brand"]}\nМодель: {data["model"]}\nГод: {data["year"]}\nОбъем: {engine}\n\nОценочная стоимость: {rec.price_usd} $\nИтоговая стоимость: {total} {currency}'
    )
    await state.clear()


@router.message(CalcStates.manual_name)
async def manual_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(CalcStates.manual_phone)
    await message.answer('Введите телефон / WhatsApp:')


@router.message(CalcStates.manual_phone)
async def manual_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(CalcStates.manual_comment)
    await message.answer('Введите комментарий:')


@router.message(CalcStates.manual_comment)
async def manual_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    comment = f"{data.get('phone', '')}; {message.text.strip()}"
    router.history.save_request(message.from_user.id, message.from_user.username or '', data.get('full_name', ''), data.get('brand', ''), data.get('model', ''), data.get('year', ''), data.get('engine', ''), comment)
    await message.answer('Спасибо! Заявка отправлена менеджеру.')
    for admin_id in settings.admin_ids:
        await router.bot.send_message(admin_id, f'Новая заявка на ручной расчет от @{message.from_user.username or message.from_user.id}')
    await state.clear()


@router.message(Command('status'))
async def status(message: Message):
    if message.from_user.id not in settings.admin_ids:
        return
    await message.answer('Бот работает.')


@router.message(Command('reload'))
async def reload_cache(message: Message):
    if message.from_user.id not in settings.admin_ids:
        return
    router.catalog.load(router.calculator.sheets.get_car_rows())
    await message.answer('Кэш обновлен.')


@router.message(Command('stats'))
async def stats(message: Message):
    if message.from_user.id not in settings.admin_ids:
        return
    await message.answer(f'Записей в кэше: {len(router.catalog.records)}')
