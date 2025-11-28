from aiogram.dispatcher.filters.state import State, StatesGroup


class Client(StatesGroup):      
    phonenumber = State()
    role=State()