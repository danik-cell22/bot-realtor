from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# === НАСТРОЙКИ ===
ADMIN_ID = 528078698  # <-- Вставь сюда свой Telegram ID от @userinfobot
BOT_TOKEN = "7981548528:AAEtJZo2yja4V_ozUhktZsvdbZZVQQoz3d4"  # <-- Токен от BotFather

# === КНОПКИ ===
main_menu = ReplyKeyboardMarkup(
    [["🏠 Недвижимость", "💼 Трудоустройство"], ["📞 Контакты"]],
    resize_keyboard=True
)

real_estate_menu = ReplyKeyboardMarkup(
    [["🏢 Квартиры", "🏡 Дома"], ["🔙 Назад"]],
    resize_keyboard=True
)

apartments_menu = ReplyKeyboardMarkup(
    [["🏗 Новостройки", "🏘 Вторичные"], ["🔙 Назад"]],
    resize_keyboard=True
)

# === СОСТОЯНИЯ ===
ASK_FORM, ASK_NEW, ASK_SECONDARY, ASK_HOUSE = range(4)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Меня зовут Юлия, я Риелтор-Руководитель.\n"
        "Помогу вам продать или купить недвижимость в Москве,\n"
        "а также найти работу в нашем агентстве 💼",
        reply_markup=main_menu
    )

# === АНКЕТА ТРУДОУСТРОЙСТВА ===
async def ask_job_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Пожалуйста, ответьте на несколько вопросов одним сообщением:\n\n"
        "1. ФИО:\n"
        "2. Возраст:\n"
        "3. Есть ли опыт в недвижимости (да/нет)?\n"
        "4. В каком районе Москвы хотите работать?\n"
        "5. Ваш Telegram или телефон для связи:\n"
    )
    return ASK_FORM

async def receive_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    msg = f"📥 Анкета от {user.full_name} (@{user.username or 'без username'}):\n\n{text}"

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        await update.message.reply_text("Спасибо! Мы с вами свяжемся в ближайшее время.", reply_markup=main_menu)
    except Exception as e:
        print("❌ Ошибка при отправке анкеты:", e)
        await update.message.reply_text("⚠️ Ошибка при отправке. Попробуйте позже.", reply_markup=main_menu)

    return ConversationHandler.END

# === ЗАЯВКИ ПО НЕДВИЖИМОСТИ ===
async def receive_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    msg = f"🏗 Заявка на новостройку от {user.full_name} (@{user.username or 'без username'}):\n{text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    await update.message.reply_text("Спасибо! Мы с вами свяжемся в ближайшее время.", reply_markup=main_menu)
    return ConversationHandler.END

async def receive_secondary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    msg = f"🏘 Заявка на вторичку от {user.full_name} (@{user.username or 'без username'}):\n{text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    await update.message.reply_text("Спасибо! Мы с вами свяжемся в ближайшее время.", reply_markup=main_menu)
    return ConversationHandler.END

async def receive_house(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    msg = f"🏡 Заявка на дом от {user.full_name} (@{user.username or 'без username'}):\n{text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    await update.message.reply_text("Спасибо! Мы с вами свяжемся в ближайшее время.", reply_markup=main_menu)
    return ConversationHandler.END

# === МЕНЮ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🏠 Недвижимость":
        await update.message.reply_text("Выберите категорию:", reply_markup=real_estate_menu)

    elif text == "📞 Контакты":
        await update.message.reply_text(
            "Связаться с нами можно по телефону: 📞 +7 927 220-13-31\n""или по почте: ✉️ Andreeva_YGe@incom.ru"
        )

    elif text == "🏢 Квартиры":
        await update.message.reply_text("Выберите тип квартиры:", reply_markup=apartments_menu)

    elif text == "🏗 Новостройки":
        await update.message.reply_text("Укажите район и желаемый бюджет:", reply_markup=None)
        return ASK_NEW

    elif text == "🏘 Вторичные":
        await update.message.reply_text("Укажите район и желаемый бюджет:", reply_markup=None)
        return ASK_SECONDARY

    elif text == "🏡 Дома":
        await update.message.reply_text("Укажите район и желаемый бюджет:", reply_markup=None)
        return ASK_HOUSE

    elif text == "🔙 Назад":
        await update.message.reply_text("Вы вернулись в главное меню:", reply_markup=main_menu)

    else:
        await update.message.reply_text("Пожалуйста, выберите пункт из меню.")

# === ЗАПУСК ===
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("💼 Трудоустройство"), ask_job_form),
        MessageHandler(filters.Regex("🏗 Новостройки"), handle_message),
        MessageHandler(filters.Regex("🏘 Вторичные"), handle_message),
        MessageHandler(filters.Regex("🏡 Дома"), handle_message),
    ],
    states={
        ASK_FORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_form)],
        ASK_NEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new)],
        ASK_SECONDARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_secondary)],
        ASK_HOUSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_house)],
    },
    fallbacks=[]
))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()