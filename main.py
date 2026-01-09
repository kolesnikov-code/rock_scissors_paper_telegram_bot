import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен бота
BOT_TOKEN = "8240375615:AAHWi2Axe2P7kC_-hhRSMzwRA20EJoGuvaw"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Состояния игры
class GameState:
    WAITING_FOR_CHOICE = "waiting_for_choice"
    GAME_OVER = "game_over"


# Хранение данных об играх
user_games = {}


# Клавиатура главного меню
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новая игра")],
            [KeyboardButton(text="Создам чат-бота для тебя")]
        ],
        resize_keyboard=True
    )
    return keyboard


# Клавиатура выбора хода
def get_choice_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🗿 Камень", callback_data="choice_rock"),
        InlineKeyboardButton(text="✂️ Ножницы", callback_data="choice_scissors"),
        InlineKeyboardButton(text="📄 Бумага", callback_data="choice_paper")
    )
    return builder.as_markup()


# Клавиатура для новой игры
def get_new_game_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔄 Новая игра", callback_data="new_game"))
    return builder.as_markup()


# Определение победителя
def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "draw"

    winning_combinations = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }

    if winning_combinations[user_choice] == bot_choice:
        return "user"
    else:
        return "bot"


# Эмодзи для выбора
choice_emojis = {
    "rock": "🗿",
    "scissors": "✂️",
    "paper": "📄"
}

# Русские названия для выбора
choice_names = {
    "rock": "Камень",
    "scissors": "Ножницы",
    "paper": "Бумага"
}


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🎮 Добро пожаловать в игру 'Камень-Ножницы-Бумага'!\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )


# Обработчик кнопки "Новая игра"
@dp.message(lambda message: message.text == "Новая игра")
async def new_game_handler(message: types.Message):
    user_id = message.from_user.id
    user_games[user_id] = {
        "state": GameState.WAITING_FOR_CHOICE,
        "mode": "bot"
    }

    # Отправляем новое сообщение с выбором хода (не редактируем предыдущее)
    await message.answer(
        "Вы играете против бота! Выберите ваш ход:",
        reply_markup=get_choice_keyboard()
    )


# Обработчик кнопки "Создам чат-бота для тебя"
@dp.message(lambda message: message.text == "Создам чат-бота для тебя")
async def create_bot_handler(message: types.Message):
    await message.answer(
        "🚀 Создам чат-бота для вашего блога, проекта и бизнеса.\n\n"

        "Взаимодействие с подписчиками и новыми пользователями, стандартные вопросы от потенциальных клиентов и готовые ответы, "
        "автоматизация продаж, круглосуточная запись на ваши услуги, интернет-магазин прямо в телеграм, ВК, Авито и MAX, "
        "ИИ-администрирование телеграм-канала и много других действий и задач, "
        "которые можно упростить и полностью автоматизировать благодаря разработке чат-бота конкретно под ваши задачи.\n\n"

        "Чат-бот никогда не устаёт, не спит, не опаздывает, не подводит вас и ваш бизнес, он работает 24/7 именно так, как вам нужно...\n\n"

        "Для получения подробной информации и заказа услуг напишите мне: @kolesnikov_developer"
    )


# Обработчик выбора хода
@dp.callback_query(lambda c: c.data.startswith('choice_'))
async def process_choice(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in user_games:
        # Если игры нет, отправляем новое сообщение с предложением начать игру
        await callback.message.answer("Сначала начните новую игру!")
        await callback.answer()
        return

    game_data = user_games[user_id]
    choice = callback.data.split('_')[1]

    # Игра против бота
    bot_choice = random.choice(["rock", "scissors", "paper"])
    result = determine_winner(choice, bot_choice)

    # Формирование сообщения с результатом
    message_text = (
        f"Ваш выбор: {choice_emojis[choice]} {choice_names[choice]}\n"
        f"Выбор бота: {choice_emojis[bot_choice]} {choice_names[bot_choice]}\n\n"
    )

    if result == "user":
        message_text += "🎉 Вы победили!"
    elif result == "bot":
        message_text += "🤖 Бот победил!"
    else:
        message_text += "🤝 Ничья!"

    # Отправляем новое сообщение с результатом (не редактируем предыдущее)
    await callback.message.answer(
        message_text,
        reply_markup=get_new_game_keyboard()
    )

    user_games[user_id]["state"] = GameState.GAME_OVER
    await callback.answer()


# Обработчик новой игры
@dp.callback_query(lambda c: c.data == "new_game")
async def new_game_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Очищаем старую игру
    if user_id in user_games:
        del user_games[user_id]

    # Создаем новую игру
    user_games[user_id] = {
        "state": GameState.WAITING_FOR_CHOICE,
        "mode": "bot"
    }

    # Отправляем новое сообщение (не редактируем предыдущее)
    await callback.message.answer(
        "Вы играете против бота! Выберите ваш ход:",
        reply_markup=get_choice_keyboard()
    )
    await callback.answer()


# Запуск бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())