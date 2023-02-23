from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    NotInitialized = State()
    Brand = State()
    Country = State()
    Ready = State()