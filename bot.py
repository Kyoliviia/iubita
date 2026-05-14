import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

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
- это мини викторина обо мне, тебе нужно отвечать правильно и честно 
- ты можешь отвечать и на румынском и на русском 
- если что ответы с маленькой буквой все, если будут с большой буквой не защитается 
- в конце тебя ждёт подарок 🎁
- желательно чтоб ты делал поменьше ошибок, а то приза тебе не видать)
"""

questions = [
    "Где была наша первая встреча?",
    "Какой мой любимый цветок?",
    "Какой мой любимый цвет?",
    "Моё любимое блюдо?",
    "Как ты меня называешь? (можешь называть одно)",
    "Как я тебя называю?",
    "Сколько мы вместе?",
    "Когда у нас особенная дата?",
    "Как мы познакомились? (не нужно рассказывать прям как, просто где или как)",
    "Во сколько лет я начала делать ногти?",
    "Мой любимый фильм? (назови только один и на русском)",
    "Кто создал эту игру?",
    "Как звали мою собаку?",
    "Во сколько я родилась?",
    "как называются таблетки которые я пью?",
    "Как зовут мою бабушку? (хотябф одну)",
    "Ты меня любишь?"
]

answers = [
    ["молдова", "молдавия", "moldova", "botna", "la botna", "in moldova", "В молдавии", "В молдове"],
    ["орхидея", "orhidee", "orhideiele", "орхидеи", "orhideea", "orhideele"],
    ["чёрный", "черный", "белый", "серый", "negru", "alb", "sur", "negru, alb, sur", "negru, sur, alb", "alb, negru,sur", "alb, sur, negru", "sur, alb, negru", "sur, negru, alb"],
    ["карбонара", "carbonara", "toate macaroanele", "macaroane", "macaroane carbonara", "все макароны"],
    ["любимая", "iubita", "iubire", "amore", "моя любимая", "Любимая, iubita, amore"],
    ["любимый", "iubitu", "iubitu, любимый ", "любимый, iubitu"],
    ["10 месяцев", "10", "10 luni", "10 luni", "10 lini si 13 zile", "10 lini si 12 zile", "10 месяцев и 13 дней"],
    ["2 июля", "2 iulie", "pe 2 iulie", "2 iulie 2025", "2 июля 2025"],
    ["онлайн", "переписка", "pe tik tok", "pe tiktok", "in conversatie", "online", "din cauza lu ruslan", "prin ruslan"],
    ["14", "la 14", "в 14", "la 14 ani", "14 ani"],
    ["Голодные игры", "Сотня", "Дивергент"],
    ["любимая девушка", "любимая", "моя любимая девушка", "iubita mea", "iubita", "prietena mea iubita", "iubita mea frumoasa", "cea mai frumosa fata din lume"],
    ["босс", "boss", "boseacu"],
    ["10", "10:00", "la ora 10:00", "la ora 10 fix", "в 10:00"],
    ["raocutan, раокутан"],
    ["евгения", "eugenia", "jenea", "sfeta", "sveta", "svetlana", "светлана", "eugenia, sfetlana", "eugenia, sfeta", "eugenia, sveta", "sfeta, eugenia", "sveta ,eugenia", "svetlana, eugenia"],
    ["да", "конечно", "разумеется", "da", "si clar", "conesna", "conesna ca te iubesc", "da te iubesc", "foarte tare"]
]

penalties = [
    "Я хирею",
    "Tu cauti sa fii batut?",
    "Ты издеваешься? Почему ты ошибаешься?",
    "Я в шоке нахрен, ты вообще любишь меня?",
    "Как ты мог ответитьнеправильно?",
    "Выбирай чем тебя лучше бить лопатой или ремнем?",
    "У меня нет слов",
    "Я не ожидала что ты сделаешь столько ошибок",
    "Нет ну это уже правда перебор тебе не кажется?",
    "Господи помоги",
    "НЕт все ты не получишь никакого подарка."
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
            await update.message.reply_text("Ладно")
            await update.message.reply_text(questions[state[user_id]])
        else:
            await finish(update)
        return

    # основная логика
    if step < len(questions):

        if text in answers[step]:

            await update.message.reply_text("Правильно")

            state[user_id] += 1

            if state[user_id] < len(questions):
                await update.message.reply_text(questions[state[user_id]])
            else:
                await finish(update)

        else:
            penalty = penalties[step % len(penalties)]

            await update.message.reply_text("Неправильно...")
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

import asyncio
asyncio.run(main())
