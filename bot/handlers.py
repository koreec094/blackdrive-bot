from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup

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
    await message.answer('Выберите страну расчета:', reply_markup=options_keyboard(['Казахстан'], 'country'))


@router.callback_query(CalcStates.choosing_country, F.data.startswith('country|'))
async def choose_country(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CalcStates.choosing_brand)
    await callback.message.answer('Выберите марку:', reply_markup=options_keyboard(router.catalog.brands(), 'brand'))


@router.callback_query(CalcStates.choosing_brand, F.data.startswith('brand|'))
async def choose_brand(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    brand = callback.data.split('|', 1)[1].strip()
    await state.update_data(brand=brand, model=None, year=None, engine=None)
    await state.set_state(CalcStates.choosing_model)
    await callback.message.answer('Выберите модель:', reply_markup=options_keyboard(router.catalog.models(brand), 'model'))


@router.callback_query(CalcStates.choosing_model, F.data.startswith('model|'))
async def choose_model(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    model = callback.data.split('|', 1)[1].strip()
    await state.update_data(model=model, year=None, engine=None)
    await state.set_state(CalcStates.choosing_year)
    await callback.message.answer('Выберите год:', reply_markup=options_keyboard(router.catalog.years(data['brand'], model), 'year'))


@router.callback_query(CalcStates.choosing_year, F.data.startswith('year|'))
async def choose_year(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    year = callback.data.split('|', 1)[1].strip()
    await state.update_data(year=year, engine=None)
    await state.set_state(CalcStates.choosing_engine)
    await callback.message.answer('Выберите объем двигателя:', reply_markup=options_keyboard(router.catalog.engines(data['brand'], data['model'], year), 'engine'))


@router.callback_query(CalcStates.choosing_engine, F.data.startswith('engine|'))
async def choose_engine(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    engine = callback.data.split('|', 1)[1].strip()
    data = await state.get_data()
    rec = router.catalog.find(data['brand'], data['model'], data['year'], engine)
    if not rec:
        await state.update_data(engine=engine)
        await state.set_state(CalcStates.manual_name)
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='Отправить контакт Telegram', request_contact=True)], [KeyboardButton(text='Написать менеджеру'), KeyboardButton(text='Вернуться к выбору автомобиля')]],
            resize_keyboard=True,
        )
        await callback.message.answer('По выбранному автомобилю нет данных для автоматического расчета.\nОставьте заявку, и менеджер сделает расчет вручную.\n\nВведите ваше имя:', reply_markup=kb)
        return

    snapshot = router.calculator.calculate(data['brand'], data['model'], data['year'], engine, rec.price_usd)
    total_line = next((row for row in snapshot if row and 'итог' in row[0].strip().lower()), None)
    total = total_line[1] if total_line and len(total_line) > 1 else '—'
    currency = total_line[2] if total_line and len(total_line) > 2 else '₸/$'

    router.history.save_success(callback.from_user.id, callback.from_user.username or '', data['brand'], data['model'], data['year'], engine, rec.price_usd, total, currency)
    await callback.message.answer(
        f'🚗 Расчет авто до Алматы\n\nМарка: {data["brand"]}\nМодель: {data["model"]}\nГод выпуска: {data["year"]}\nОбъем двигателя: {engine}\n\nОценочная стоимость / инвойс: {rec.price_usd} $\n\nИтоговая стоимость авто в Алматы с таможней:\n{total} {currency}'
    )
    await state.clear()


@router.message(CalcStates.manual_name)
async def manual_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(CalcStates.manual_phone)
    await message.answer('Введите телефон / WhatsApp:')


@router.message(CalcStates.manual_phone)
async def manual_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else (message.text or '').strip()
    await state.update_data(phone=phone)
    await state.set_state(CalcStates.manual_comment)
    await message.answer('Введите комментарий:')


@router.message(CalcStates.manual_comment)
async def manual_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    router.history.save_request(
        message.from_user.id,
        message.from_user.username or '',
        data.get('full_name', ''),
        data.get('brand', ''),
        data.get('model', ''),
        data.get('year', ''),
        data.get('engine', ''),
        data.get('phone', ''),
        message.text.strip(),
    )
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
    await message.answer(f'Записей в кэше: {len(router.catalog.records)}\nРасчетов: {router.history.history_count()}\nЗаявок: {router.history.requests_count()}')
