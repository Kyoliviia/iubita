import logging
import nest_asyncio
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

nest_asyncio.apply()

TOKEN = "8757169873:AAHYn_cV6tcZrBZPpF4ZWWP-kPp1ftouNkA"

logging.basicConfig(level=logging.INFO)

state = {}
waiting_penalty = {}

menu = ReplyKeyboardMarkup(
    [["▶ Начать игру", "📜 Правила"], ["❌ Выход"]],
    resize_keyboard=True
)

rules_text = """
📜 ПРАВИЛА:
- отвечай честно 💞
- за ошибки будут романтические задания 😏
- в конце тебя ждёт подарок 🎁
"""

questions = [
    "Где была наша первая встреча?",
    "Какой мой любимый цветок?",
    "Какой мой любимый цвет?",
    "Моё любимое блюдо?",
    "Как ты меня называешь?",
    "Как я тебя называю?",
    "Сколько мы вместе?",
    "Когда у нас особенная дата?",
    "Как мы познакомились?",
    "Где была наша первая встреча?",
    "Что ты должен получить в конце игры?",
    "Кто создал эту игру?",
    "Что я чувствую к тебе?",
    "Кто ты для меня?",
    "Что самое важное между нами?",
    "Что ты должен сделать после игры?",
    "Что я для тебя?",
    "Что ты должен сделать сейчас?"
]

answers = [
    ["молдова", "Молдавия"],
    ["орхидея"],
    ["чёрный", "черный"],
    ["карбонара"],
    ["любимая"],
    ["любимый"],
    ["10 месяцев", "10"],
    ["2 июля"],
    ["онлайн", "переписка"],
    ["молдова"],
    ["keepsafe"],
    ["любимая девушка", "Любимая"],
    ["любовь", "симпатию"],
    ["любимый"],
    ["доверие", "связь"],
    ["скачать keepsafe", "keepsafe"],
    ["любовь", "Жизнь", "Всё", "Все"],
    ["принять награду"]
]

penalties = [
    "Расскажи, почему ты меня любишь 😏",
    "Что тебе во мне больше всего нравится?",
    "Ты издеваешься? Почему ты ошибаешься?",
    "Я в шоке нахрен, ты вообще любишь меня?",
    "Докажи, что ты скучаешь по мне 💞",
    "Почему ты выбрал именно меня?",
    "Что бы ты сделал ради меня?"
]

def normalize(text):
    return text.lower().strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state[user_id] = 0
    waiting_penalty[user_id] = False

    await update.message.reply_text(
        "🔐 SECRET LOVE MISSION АКТИВИРОВАНА...\n\n"
        "Это игра от твоей любимой девушки 💞\n"
        "Покажи, насколько хорошо ты её знаешь 😏",
        reply_markup=menu
    )

async def finish(update: Update):
    await update.message.reply_text(
        "🔓 ДОСТУП ОТКРЫТ...\n\n"
        "💞 Поздравляю...\n"
        "Ты прошёл Secret Love Mission.\n\n"
        "🎁 НАГРАДА:\n"
        "📱 Приложение: Keepsafe\n\n"
        "🔐 Код даст тебе твоя любимая девушка 😏💞"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = normalize(update.message.text)

    if user_id not in state:
        state[user_id] = 0
        waiting_penalty[user_id] = False

    step = state[user_id]

    if text == "📜 правила":
        await update.message.reply_text(rules_text)
        return

    if text == "❌ выход":
        await update.message.reply_text("💞 Я всё равно тебя люблю...")
        return

    if text == "▶ начать игру":
        state[user_id] = 0
        waiting_penalty[user_id] = False
        await update.message.reply_text("💌 Начнём...")
        await update.message.reply_text(questions[0])
        return

    # если отвечает на штраф
    if waiting_penalty[user_id]:
        waiting_penalty[user_id] = False
        state[user_id] += 1

        if state[user_id] < len(questions):
            await update.message.reply_text("💞 Принято… идём дальше 😏")
            await update.message.reply_text(questions[state[user_id]])
        else:
            await finish(update)
        return

    # основная логика
    if step < len(questions):

        if text in answers[step]:

            await update.message.reply_text("💞 Молодец… ты всё помнишь 😏")

            state[user_id] += 1

            if state[user_id] < len(questions):
                await update.message.reply_text(questions[state[user_id]])
            else:
                await finish(update)

        else:
            penalty = penalties[step % len(penalties)]

            await update.message.reply_text("😏 Неправильно...")
            await update.message.reply_text("💌 " + penalty)

            waiting_penalty[user_id] = True

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🤖 Бот запущен...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(10)

await main()
