from telebot import types, TeleBot, StateMemoryStorage
from telebot.custom_filters import StateFilter
import states, texts, keyboards


bot = TeleBot(token='7434782071:AAFvoBm13N_ZQbimxuHV21fXiQ3YSAV3dqs',
              state_storage=StateMemoryStorage(),
              parse_mode='HTML')


def check_state(message, state):
    print(bot.get_state(message.from_user.id, message.chat.id))
    if bot.get_state(message.from_user.id, message.chat.id) == state:
        return True
    return False

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.delete_message(message.chat.id, message.id)
    bot.send_message(message.chat.id, texts.start_text)
    bot.set_state(message.from_user.id, states.MainStates.main, message.chat.id)
    # TODO Аутентификация


@bot.message_handler(commands=['main'], state=[states.MainStates.main])
def main(message: types.Message):
    text = texts.main_text
    # TODO Запрос данных
    # text.format()

    bot.send_message(message.chat.id, text, reply_markup=keyboards.main_keyboard)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('habits'))
def habits_view(callback: types.CallbackQuery):
    text = texts.habits_text
    habits_pagination = int(callback.data.removeprefix('habits')) if callback.data != 'habits' else 0
    habits_numeration = habits_pagination * 10

    keyboard = types.InlineKeyboardMarkup()
    end_row = []
    previous_habits = types.InlineKeyboardButton('<-', callback_data='habits{page}'.format(page=habits_pagination-1)) if habits_numeration != 0 else None
    # TODO Запрос на кол-во привычек пользвателя
    next_habits = types.InlineKeyboardButton('->', callback_data='habits{page}'.format(page=habits_pagination+1)) if 'habits_count' - habits_numeration != 10 else None
    if previous_habits:
        end_row.append(previous_habits)
    end_row.append(keyboards.create_habit_button)
    if next_habits:
        end_row.append(next_habits)

    # TODO Запрос привычек
    habits = []
    if habits:
        row = []
        for habit in habits:
            text += '\n{index} | {title} | {process}'
            row.append(types.InlineKeyboardButton('{title}', callback_data='habit{idx}-{page}'.format(idx='habit.id', page=habits_pagination)))
            if len(row) == 2:
                keyboard.row(*row)
                row.clear()
            elif habits.index(habit) == len(habits) - 1:
                keyboard.row(*row)

    else:
        text += '\nУ тебя пока нет активных привычек'
    keyboard.row(*end_row)
    bot.edit_message_text(text, callback.message.chat.id, callback.message.id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: callback.data == 'create')
def create_habit(callback: types.CallbackQuery):
    bot.edit_message_text(texts.create_habit_text, callback.message.chat.id, callback.message.id)
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data['main_message_id'] = callback.message.id
    bot.set_state(callback.from_user.id, states.CreateHabitStates.title, callback.message.chat.id)


@bot.message_handler(state=states.CreateHabitStates.title)
def set_title_for_habit(message: types.Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['title'] = message.text
        main_id = data['main_message_id']
    text = "Отлично! Давай теперь придумаем описание для привычки."

    bot.edit_message_text(text, message.chat.id, main_id)
    bot.set_state(message.from_user.id, states.CreateHabitStates.description, message.chat.id)


@bot.message_handler(state=states.CreateHabitStates.description)
def set_description_for_habit(message: types.Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['description'] = message.text
        main_id = data['main_message_id']
    # TODO Запрос на создание привычки
    text = 'Привычка отслеживается.'
    bot.edit_message_text(text, message.chat.id, main_id, reply_markup=keyboards.back_keyboard)
    bot.set_state(message.from_user.id, states.MainStates.main, message.chat.id)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('habit'))
def habit_view(callback: types.CallbackQuery):
    text = texts.habit_text
    idx, page = tuple(callback.data.removeprefix('habit').split('-'))
    idx, page = int(idx), int(page)
    # TODO Запрос привычки
    # text.format()
    keyboard = types.InlineKeyboardMarkup()
    edit_title = types.InlineKeyboardButton('Изменить название', callback_data='title{idx}-{page}'.format(idx=idx, page=page))
    edit_description = types.InlineKeyboardButton('Изменить описание', callback_data='desc{idx}-{page}'.format(idx=idx, page=page))
    keyboard.row(edit_title).row(edit_description)
    back_button = types.InlineKeyboardButton('Вернуться', callback_data='habits{page}'.format(page=page))
    keyboard.row(back_button)
    bot.edit_message_text(text, callback.message.chat.id, callback.message.id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('title'))
def edit_title(callback: types.CallbackQuery):
    idx, page = tuple(callback.data.removeprefix('habit').split('-'))
    text = 'Введи новое название'
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data['main_message_id'] = callback.message.id
        data['habit_id'] = idx
        data['page'] = page
    bot.edit_message_text(text, callback.message.chat.id, callback.message.id)
    bot.set_state(callback.from_user.id, states.EditHabitStates.title, callback.message.chat.id)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('desc'))
def edit_description(callback: types.CallbackQuery):
    idx, page = tuple(callback.data.removeprefix('habit').split('-'))
    text = 'Введи новое описание'
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data['main_message_id'] = callback.message.id
        data['habit_id'] = idx
        data['page'] = page
    bot.edit_message_text(text, callback.message.chat.id, callback.message.id)
    bot.set_state(callback.from_user.id, states.EditHabitStates.description, callback.message.chat.id)


@bot.message_handler(state=states.EditHabitStates.title)
def apply_new_title(message: types.Message):
    name = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        idx = data['habit_id']
        page = data['page']
        main_id = data['main_message_id']
    # TODO изменить привычку
    back_keyboard = types.InlineKeyboardMarkup()
    back_keyboard.add(types.InlineKeyboardButton('Вернуться', callback_data='habit{idx}-{page}'.format(idx=idx, page=page)))
    bot.edit_message_text('Изменения успешно применены!', message.chat.id, message.id, reply_markup=back_keyboard)
    bot.set_state(message.from_user.id, states.MainStates.main, message.chat.id)


@bot.message_handler(state=states.EditHabitStates.description)
def apply_new_description(message: types.Message):
    description = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        idx = data['habit_id']
        page = data['page']
        main_id = data['main_message_id']
    # TODO изменить привычку
    back_keyboard = types.InlineKeyboardMarkup()
    back_keyboard.add(types.InlineKeyboardButton('Вернуться', callback_data='habit{idx}-{page}'.format(idx=idx, page=page)))
    bot.edit_message_text('Изменения успешно применены!', message.chat.id, main_id, reply_markup=back_keyboard)
    bot.set_state(message.from_user.id, states.MainStates.main, message.chat.id)


if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    bot.infinity_polling(skip_pending=True)
