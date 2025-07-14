import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# === Загрузка .env ===
load_dotenv()
BOT_TOKEN = os.getenv("7981548528:AAEtJZo2yja4V_ozUhktZsvdbZZVQQoz3d4")
ADMIN_ID = int(os.getenv("1102710517"))

# === Логирование ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
        await update.message.reply_text(
            "Здравствуйте! Меня зовут Юлия, я Риелтор-Руководитель.\n"
            "Помогу вам продать или купить недвижимость в Москве,\n"
            "а также найти работу в нашем агентстве 💼",
            reply_markup=main_menu
        )
    except Exception as e:
        logger.error("Ошибка при старте: %s", e)
        await update.message.reply_text("⚠️ Ошибка при отправке. Попробуйте позже.")

# === МЕНЮ И СОСТОЯНИЯ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        match text:
            case "🏠 Недвижимость":
                await update.message.reply_text("Выберите категорию:", reply_markup=real_estate_menu)

            case "📞 Контакты":
                await update.message.reply_text(
                    "Связаться с нами можно по телефону: 📞 +7 927 220-13-31\n"
                    "или по почте: ✉️ Andreeva_YGe@incom.ru"
                )

            case "🏢 Квартиры":
                await update.message.reply_text("Выберите тип квартиры:", reply_markup=apartments_menu)

            case "🏗 Новостройки":
                await update.message.reply_text("Укажите район и желаемый бюджет:")
                return ASK_NEW

            case "🏘 Вторичные":
                await update.message.reply_text("Укажите район и желаемый бюджет:")
                return ASK_SECONDARY

            case "🏡 Дома":
                await update.message.reply_text("Укажите район и желаемый бюджет:")
                return ASK_HOUSE

            case "💼 Трудоустройство":
                await update.message.reply_text(
                    "Пожалуйста, ответьте на несколько вопросов одним сообщением:\n\n"
                    "1. ФИО:\n"
                    "2. Возраст:\n"
                    "3. Есть ли опыт в недвижимости (да/нет)?\n"
                    "4. В каком районе Москвы хотите работать?\n"
                    "5. Ваш Telegram или телефон для связи:"
                )
                return ASK_FORM

            case "🔙 Назад":
                await update.message.reply_text("Вы вернулись в главное меню:", reply_markup=main_menu)

            case _:
                await update.message.reply_text("Пожалуйста, выберите пункт из меню.")

    except Exception as e:
        logger.error("Ошибка при выводе сообщения: %s", e)
        await update.message.reply_text("⚠️ Ошибка при отправке. Попробуйте позже.")

# === ОБРАБОТКА АНКЕТ И ЗАЯВОК ===
async def receive_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await forward_response(update, context, "📥 Анкета")

async def receive_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await forward_response(update, context, "🏗 Заявка на новостройку")

async def receive_secondary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await forward_response(update, context, "🏘 Заявка на вторичку")

async def receive_house(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await forward_response(update, context, "🏡 Заявка на дом")

# === ОБЩАЯ ФУНКЦИЯ ОТПРАВКИ ЗАЯВОК ===
async def forward_response(update: Update, context: ContextTypes.DEFAULT_TYPE, title: str):
    user = update.message.from_user
    text = update.message.text
    msg = f"{title} от {user.full_name} (@{user.username or 'без username'}):\n\n{text}"

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        await update.message.reply_text("Спасибо! Мы с вами свяжемся в ближайшее время.", reply_markup=main_menu)
    except Exception as e:
        logger.error("Ошибка при отправке анкеты: %s", e)
        await update.message.reply_text("⚠️ Ошибка при отправке. Попробуйте позже.", reply_markup=main_menu)

    return ConversationHandler.END

# === ОТМЕНА ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Операция отменена.", reply_markup=main_menu)
    except Exception as e:
        logger.error("Ошибка при отмене: %s", e)
        await update.message.reply_text("⚠️ Ошибка при отправке. Попробуйте позже.")
    return ConversationHandler.END

# === ЗАПУСК ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            ASK_FORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_form)],
            ASK_NEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new)],
            ASK_SECONDARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_secondary)],
            ASK_HOUSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_house)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    logger.info("🤖 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
