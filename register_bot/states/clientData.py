from aiogram.dispatcher.filters.state import State, StatesGroup


class Client(StatesGroup):
    lang = State()
    phone_number = State()
    role = State()
    name = State()
    location = State()
    lump_sum = State()
   
    
