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


# Состояния игры...
class GameState:
    WAITING_FOR_CHOICE = "waiting_for_choice"
    WAITING_FOR_OPPONENT = "waiting_for_opponent"
    GAME_OVER = "game_over"


# Хранение данных об играх
user_games = {}
multiplayer_games = {}


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


# Клавиатура выбора режима игры
def get_game_mode_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🤖 Против бота", callback_data="mode_bot"),
        InlineKeyboardButton(text="👥 Против человека", callback_data="mode_multiplayer")
    )
    return builder.as_markup()


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
    await message.answer(
        "Выберите режим игры:",
        reply_markup=get_game_mode_keyboard()
    )


# Обработчик кнопки "Создам чат-бота для тебя"
@dp.message(lambda message: message.text == "Создам чат-бота для тебя")
async def create_bot_handler(message: types.Message):
    await message.answer(
        "🚀 Создам чат-бота для вашего блога, проекта и бизнеса.\n\n"

        "Взаимодействие с подписчиками и новыми пользователями, стандартные вопросы от потенциальных клиентов и готовые ответы, "
        "автоматизация продаж, круглосуточная запись на ваши услуги, интернет-магазин прямо в телеграм, ВК, Авито и MAX, "
        "ИИ-администрирование телеграм-канала и много, много, очень много других действий и задач, "
        "которые можно упростить и полностью автоматизировать благодаря разработке чат-бота конкретно под ваши задачи.\n\n"

        "Чат-бот никогда не устаёт, не спит, не опаздывает, не подводит вас и ваш бизнес, он работает 24/7 именно так, как вам нужно...\n\n"

        "Для получения подробной информации и заказа услуг свяжитесь со мной: @kolesnikov_developer"
    )


# Обработчик выбора режима игры
@dp.callback_query(lambda c: c.data.startswith('mode_'))
async def process_game_mode(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    mode = callback.data.split('_')[1]

    if mode == "bot":
        user_games[user_id] = {
            "state": GameState.WAITING_FOR_CHOICE,
            "mode": "bot"
        }

        await callback.message.edit_text(
            "Вы играете против бота! Выберите ваш ход:",
            reply_markup=get_choice_keyboard()
        )

    elif mode == "multiplayer":
        # Поиск ожидающей игры или создание новой
        found_game = None
        for game_id, game_data in multiplayer_games.items():
            if game_data["player2"] is None and game_data["player1"] != user_id:
                found_game = game_id
                break

        if found_game:
            # Присоединение к существующей игре
            multiplayer_games[found_game]["player2"] = user_id
            multiplayer_games[found_game]["state"] = GameState.WAITING_FOR_CHOICE

            user_games[user_id] = {
                "game_id": found_game,
                "state": GameState.WAITING_FOR_CHOICE,
                "mode": "multiplayer",
                "is_player1": False
            }

            # Уведомление обоих игроков
            player1_id = multiplayer_games[found_game]["player1"]
            await bot.send_message(
                player1_id,
                "Противник найден! Выберите ваш ход:",
                reply_markup=get_choice_keyboard()
            )

            await callback.message.edit_text(
                "Противник найден! Выберите ваш ход:",
                reply_markup=get_choice_keyboard()
            )

        else:
            # Создание новой игры
            game_id = str(user_id) + str(random.randint(1000, 9999))
            multiplayer_games[game_id] = {
                "player1": user_id,
                "player2": None,
                "choices": {},
                "state": GameState.WAITING_FOR_OPPONENT
            }

            user_games[user_id] = {
                "game_id": game_id,
                "state": GameState.WAITING_FOR_OPPONENT,
                "mode": "multiplayer",
                "is_player1": True
            }

            await callback.message.edit_text(
                "🔍 Ожидаем второго игрока...\n"
                "Поделитесь этой игрой с другом!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_waiting")
                ]])
            )

    await callback.answer()


# Обработчик обновления ожидания
@dp.callback_query(lambda c: c.data == "refresh_waiting")
async def refresh_waiting(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id in user_games and user_games[user_id]["mode"] == "multiplayer":
        game_id = user_games[user_id]["game_id"]

        if multiplayer_games[game_id]["player2"]:
            await callback.message.edit_text(
                "Противник найден! Выберите ваш ход:",
                reply_markup=get_choice_keyboard()
            )
        else:
            await callback.answer("Все еще ждем второго игрока...")
    else:
        await callback.answer("Игра не найдена")


# Обработчик выбора хода
@dp.callback_query(lambda c: c.data.startswith('choice_'))
async def process_choice(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in user_games:
        await callback.answer("Сначала начните новую игру!")
        return

    game_data = user_games[user_id]
    choice = callback.data.split('_')[1]

    if game_data["mode"] == "bot":
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

        await callback.message.edit_text(
            message_text,
            reply_markup=get_new_game_keyboard()
        )

        user_games[user_id]["state"] = GameState.GAME_OVER

    elif game_data["mode"] == "multiplayer":
        # Мультиплеерная игра
        game_id = game_data["game_id"]
        multiplayer_data = multiplayer_games[game_id]

        # Сохраняем выбор игрока
        player_key = "player1" if game_data["is_player1"] else "player2"
        multiplayer_data["choices"][player_key] = choice

        # Проверяем, сделали ли оба хода
        if len(multiplayer_data["choices"]) == 2:
            # Оба игрока сделали ход
            choice1 = multiplayer_data["choices"]["player1"]
            choice2 = multiplayer_data["choices"]["player2"]

            result = determine_winner(choice1, choice2)

            # Формируем сообщения для обоих игроков
            player1_id = multiplayer_data["player1"]
            player2_id = multiplayer_data["player2"]

            message_text = (
                f"Ваш выбор: {choice_emojis[choice1]} {choice_names[choice1]}\n"
                f"Выбор противника: {choice_emojis[choice2]} {choice_names[choice2]}\n\n"
            )

            if result == "user":
                message_text_player1 = message_text + "🎉 Вы победили!"
                message_text_player2 = message_text + "😢 Вы проиграли!"
            elif result == "bot":  # Здесь "bot" означает, что победил второй игрок
                message_text_player1 = message_text + "😢 Вы проиграли!"
                message_text_player2 = message_text + "🎉 Вы победили!"
            else:
                message_text_player1 = message_text + "🤝 Ничья!"
                message_text_player2 = message_text + "🤝 Ничья!"

            # Отправляем результаты
            await bot.send_message(
                player1_id,
                message_text_player1,
                reply_markup=get_new_game_keyboard()
            )

            await bot.send_message(
                player2_id,
                message_text_player2,
                reply_markup=get_new_game_keyboard()
            )

            # Обновляем состояние
            user_games[player1_id]["state"] = GameState.GAME_OVER
            user_games[player2_id]["state"] = GameState.GAME_OVER

            # Удаляем игру из multiplayer_games
            del multiplayer_games[game_id]

        else:
            # Ждем ход второго игрока
            await callback.answer("Ход принят! Ждем противника...")
            return

    await callback.answer()


# Обработчик новой игры
@dp.callback_query(lambda c: c.data == "new_game")
async def new_game_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Очищаем старую игру
    if user_id in user_games:
        # Если это мультиплеер и игра еще активна, удаляем ее
        if user_games[user_id]["mode"] == "multiplayer" and user_games[user_id]["state"] != GameState.GAME_OVER:
            game_id = user_games[user_id]["game_id"]
            if game_id in multiplayer_games:
                del multiplayer_games[game_id]

        del user_games[user_id]

    await callback.message.edit_text(
        "Выберите режим игры:",
        reply_markup=get_game_mode_keyboard()
    )
    await callback.answer()


# Запуск бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())