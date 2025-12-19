from aiogram.fsm.state import State, StatesGroup

class AppStates(StatesGroup):
    waiting_for_teacher = State()
    waiting_for_course_name = State()
    waiting_for_course_link = State()