from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


main_keyboard = InlineKeyboardMarkup()
main_keyboard.row(
    InlineKeyboardButton('Просмотр привычек', callback_data='habits'),
    InlineKeyboardButton('Настройки', callback_data='settings')
)
create_habit_button = InlineKeyboardButton('Создать новую привычку', callback_data='create')

back_keyboard = InlineKeyboardMarkup()
back_keyboard.add(InlineKeyboardButton('Вернуться к привычкам', callback_data='habits'))
