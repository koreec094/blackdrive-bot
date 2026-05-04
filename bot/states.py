from aiogram.fsm.state import State, StatesGroup


class CalcStates(StatesGroup):
    choosing_country = State()
    choosing_brand = State()
    choosing_model = State()
    choosing_year = State()
    choosing_engine = State()
    manual_name = State()
    manual_phone = State()
    manual_comment = State()
