from aiogram.fsm.state import State, StatesGroup

class GZState(StatesGroup):
    base_url = State()
    prompt = State()
