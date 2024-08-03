from telebot.handler_backends import State, StatesGroup


class MainStates(StatesGroup):
    main = State()


class CreateHabitStates(StatesGroup):
    title = State()
    description = State()


class EditHabitStates(StatesGroup):
    title = State()
    description = State()
