from aiogram.dispatcher.filters.state import State, StatesGroup


class Client(StatesGroup):      
    lang = State()
    role=State()