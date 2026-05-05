from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup

from bot.config import settings
from bot.keyboards import options_keyboard, start_menu_keyboard, subscribe_keyboard
from bot.states import CalcStates


router = Router()
logger = logging.getLogger(__name__)


def digits_only(value: str) -> str:
    return ''.join(ch for ch in (value or '') if ch.isdigit())


def find_value(snapshot: list[list[str]], *keywords: str) -> str:
    lowered = [k.casefold() for k in keywords]
    for row in snapshot:
        if not row:
            continue
        label = (row[0] if len(row) > 0 else '').strip().casefold()
        if any(k in label for k in lowered):
            return (row[1] if len(row) > 1 else '').strip() or '—'
    return '—'


def register_dependencies(catalog, calculator, history, bot):
    router.catalog = catalog
    router.calculator = calculator
    router.history = history
    router.bot = bot


async def render_start_menu(message: Message, state: FSMContext, edit: bool = False):
    await state.clear()
    await state.set_state(CalcStates.choosing_country)
    text = 'Выберите действие:'
    kb = start_menu_keyboard(settings.main_channel_url)
    if edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


async def check_subscription(user_id: int) -> bool:
    if not settings.main_channel_id:
        return True
    try:
        member = await router.bot.get_chat_member(chat_id=settings.main_channel_id, user_id=user_id)
        return member.status in {'creator', 'administrator', 'member'}
    except Exception as exc:
        logger.warning('Subscription check failed: %s', exc)
        return False


@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    await render_start_menu(message, state)


@router.callback_query(CalcStates.choosing_country, F.data == 'menu|manager')
async def manager_contacts(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        f'Связаться с менеджером:\nTelegram: {settings.manager_telegram}\nWhatsApp: {settings.manager_whatsapp}'
    )


@router.callback_query(CalcStates.choosing_country, F.data == 'menu|calculate')
async def start_calculation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await check_subscription(callback.from_user.id):
        await callback.message.edit_text(
            'Чтобы пользоваться расчетом, подпишитесь на наш канал.',
            reply_markup=subscribe_keyboard(settings.main_channel_url),
        )
        return
    await state.set_state(CalcStates.choosing_brand)
    await callback.message.edit_text('Выберите марку:', reply_markup=options_keyboard(router.catalog.brands(), 'brand'))


@router.callback_query(CalcStates.choosing_country, F.data == 'menu|check_subscription')
async def recheck_subscription(callback: CallbackQuery, state: FSMContext):
    await start_calculation(callback, state)


@router.callback_query(CalcStates.choosing_country, F.data == 'menu|back_to_start')
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await render_start_menu(callback.message, state, edit=True)


@router.callback_query(CalcStates.choosing_brand, F.data.startswith('brand|'))
async def choose_brand(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    brand = callback.data.split('|', 1)[1].strip()
    await state.update_data(brand=brand, model=None, year=None, engine=None, car_price_krw=None)
    await state.set_state(CalcStates.choosing_model)
    await callback.message.edit_text(
        'Выберите модель:',
        reply_markup=options_keyboard(router.catalog.models(brand), 'model', with_back=True, back_callback='nav|to_brand'),
    )


@router.callback_query(CalcStates.choosing_model, F.data == 'nav|to_brand')
async def back_to_brand(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(model=None, year=None, engine=None, car_price_krw=None)
    await state.set_state(CalcStates.choosing_brand)
    await callback.message.edit_text('Выберите марку:', reply_markup=options_keyboard(router.catalog.brands(), 'brand'))


@router.callback_query(CalcStates.choosing_model, F.data.startswith('model|'))
async def choose_model(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    model = callback.data.split('|', 1)[1].strip()
    await state.update_data(model=model, year=None, engine=None, car_price_krw=None)
    await state.set_state(CalcStates.choosing_year)
    await callback.message.edit_text(
        'Выберите год:',
        reply_markup=options_keyboard(router.catalog.years(data['brand'], model), 'year', with_back=True, back_callback='nav|to_model'),
    )


@router.callback_query(CalcStates.choosing_year, F.data == 'nav|to_model')
async def back_to_model(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await state.update_data(year=None, engine=None, car_price_krw=None)
    await state.set_state(CalcStates.choosing_model)
    await callback.message.edit_text(
        'Выберите модель:',
        reply_markup=options_keyboard(router.catalog.models(data['brand']), 'model', with_back=True, back_callback='nav|to_brand'),
    )


@router.callback_query(CalcStates.choosing_year, F.data.startswith('year|'))
async def choose_year(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    year = callback.data.split('|', 1)[1].strip()
    await state.update_data(year=year, engine=None, car_price_krw=None)
    await state.set_state(CalcStates.choosing_engine)
    await callback.message.edit_text(
        'Выберите объем двигателя:',
        reply_markup=options_keyboard(
            router.catalog.engines(data['brand'], data['model'], year), 'engine', with_back=True, back_callback='nav|to_year'
        ),
    )


@router.callback_query(CalcStates.choosing_engine, F.data == 'nav|to_year')
async def back_to_year(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await state.update_data(engine=None, car_price_krw=None)
    await state.set_state(CalcStates.choosing_year)
    await callback.message.edit_text(
        'Выберите год:',
        reply_markup=options_keyboard(router.catalog.years(data['brand'], data['model']), 'year', with_back=True, back_callback='nav|to_model'),
    )


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

    await state.update_data(engine=engine, invoice_usd=rec.price_usd)
    await state.set_state(CalcStates.entering_real_price)
    await callback.message.edit_text('Введите стоимость автомобиля в Корее в KRW', reply_markup=options_keyboard([], 'noop', with_back=True, back_callback='nav|to_engine'))


@router.callback_query(CalcStates.entering_real_price, F.data == 'nav|to_engine')
async def back_to_engine(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await state.update_data(car_price_krw=None)
    await state.set_state(CalcStates.choosing_engine)
    await callback.message.edit_text(
        'Выберите объем двигателя:',
        reply_markup=options_keyboard(router.catalog.engines(data['brand'], data['model'], data['year']), 'engine', with_back=True, back_callback='nav|to_year'),
    )


@router.message(CalcStates.entering_real_price)
async def enter_real_price(message: Message, state: FSMContext):
    real_price_krw = digits_only(message.text or '')
    if not real_price_krw:
        await message.answer('Не удалось распознать сумму. Введите стоимость в KRW, например: 485500000')
        return

    data = await state.get_data()
    snapshot = router.calculator.calculate(data['brand'], data['model'], data['year'], data['engine'], data['invoice_usd'], real_price_krw)
    total_line = next((row for row in snapshot if row and 'итог' in row[0].strip().lower()), None)
    total = total_line[1] if total_line and len(total_line) > 1 else '—'
    currency = total_line[2] if total_line and len(total_line) > 2 else '₸/$'

    car_to_almaty_krw = find_value(snapshot, 'стоимость автомобиля до алматы', 'авто до алматы')
    car_to_almaty_usd = find_value(snapshot, 'стоимость автомобиля до алматы usd', 'авто до алматы usd')
    if settings.car_to_almaty_total_cell:
        cell_value = router.calculator.sheets.read_calc_cell(settings.car_to_almaty_total_cell)
        if cell_value:
            car_to_almaty_krw = cell_value
        else:
            logger.warning('Cell %s for car to Almaty total is empty', settings.car_to_almaty_total_cell)
            if car_to_almaty_krw in {'', '—'}:
                car_to_almaty_krw = 'не рассчитано'

    fees = find_value(snapshot, 'сборы')
    duty = find_value(snapshot, 'пошлина')
    vat = find_value(snapshot, 'ндс')
    recycle = find_value(snapshot, 'утильсбор')
    reg = find_value(snapshot, 'первичная регистрация')
    sbkts = find_value(snapshot, 'сбктс', 'эптс', 'кнопка')

    router.history.save_success(message.from_user.id, message.from_user.username or '', data['brand'], data['model'], data['year'], data['engine'], data['invoice_usd'], total, currency)
    await message.answer(
        f'🚗 Расчет авто до Алматы\n\n'
        f'Марка: {data["brand"]}\n'
        f'Модель: {data["model"]}\n'
        f'Год выпуска: {data["year"]}\n'
        f'Объем двигателя: {data["engine"]}\n\n'
        f'Реальная стоимость авто в Корее: {real_price_krw} ₩\n'
        f'Комиссия дилера: 440 000 ₩\n'
        f'Логистика Инчон — Алматы: 1 750 $\n'
        f'Стоимость автомобиля до Алматы: {car_to_almaty_krw} ₩ / {car_to_almaty_usd} $\n'
        f'Оценочная стоимость / инвойс для таможни: {data["invoice_usd"]} $\n\n'
        f'Сборы: {fees}\n'
        f'Пошлина: {duty}\n'
        f'НДС: {vat}\n'
        f'Утильсбор: {recycle}\n'
        f'Первичная регистрация: {reg}\n'
        f'СБКТС/ЭПТС/Кнопка: {sbkts}\n\n'
        f'Итоговая стоимость авто в Алматы с таможней:\n{total} {currency}\n\n'
        f'Связаться с нами:\nTelegram: {settings.manager_telegram}\nWhatsApp: {settings.manager_whatsapp}'
    )
    await state.clear()

# other handlers unchanged...
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
