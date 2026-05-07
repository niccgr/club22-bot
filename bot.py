import datetime
from telegram import Bot, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update

# ══════════════════════════════════════════
#  НАСТРОЙКИ
# ══════════════════════════════════════════
BOT_TOKEN   = "8686292524:AAHMoMyW8gwnD_JkcZrOEObq3HL13KAZtM4"
GROUP_NAME  = "Клуб 22"
PASSWORD    = "1221"
MINIAPP_URL = "https://effortless-panda-3b18f1.netlify.app/"

# ══════════════════════════════════════════
#  СПИСОК ДР
# ══════════════════════════════════════════
BIRTHDAYS = [
    ("@zbelitsyna",         "Зиночка",  5,  12, "f"),
    ("@Merpert",            "Стёпа",    5,  20, "m"),
    ("@oioantonio",         "Антон",    7,  14, "m"),
    ("@daria_shushanikova", "Дашуля",   8,  12, "f"),
    ("@Good4twenty",        "Лёша",     9,   1, "m"),
    ("@margotornot",        "Ритусик",  9,   9, "f"),
    ("@lsthedstnc",         "Луиза",   10,  30, "f"),
    ("@Vero_4_ka",          "Верочка", 12,   1, "f"),
    ("@Yaremad",            "Андрей",  12,   2, "m"),
    ("@GdKnowledge",        "Женя",    12,  14, "m"),
    ("@valeriy_komarov",    "Валера",  12,  19, "m"),
    ("@la_confidential",    "Ник",     12,  21, "m"),
    ("@setabad",            "Света",    1,  14, "f"),
    ("@grevtsovtimur",      "Тимур",    1,  22, "m"),
    ("@loctar_o_gar",       "Руслан",   2,  12, "m"),
    ("@Stal999",            "Влад",     3,  13, "m"),
    ("@Randepuk",           "Юра",      3,  18, "m"),
    ("@Marussiaspring",     "Маруся",   4,  17, "f"),
    ("@yesley",             "Ярик",     5,   4, "m"),
]

MONTH_NAMES = ["","января","февраля","марта","апреля","мая","июня",
               "июля","августа","сентября","октября","ноября","декабря"]

# Хранилище авторизованных пользователей (chat_id -> True)
# Сбрасывается при перезапуске — для постоянного хранения нужна БД
authorized_users: set = set()
# Пользователи которые ввели /start но ещё не ввели пароль
waiting_password: set = set()

# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════
def days_until(month, day):
    today = datetime.date.today()
    next_bd = datetime.date(today.year, month, day)
    if next_bd < today:
        next_bd = datetime.date(today.year + 1, month, day)
    return (next_bd - today).days

def format_days(n):
    if n == 0: return "сегодня 🎂"
    if n == 1: return "завтра"
    if 2 <= n <= 4: return f"через {n} дня"
    return f"через {n} дней"

def welcome_text():
    return (
        f"👋 Привет! Я бот <b>{GROUP_NAME}</b>.\n\n"
        f"Слежу за днями рождения и буду напоминать тебе "
        f"в личку за 3 дня и за 1 день до каждого праздника.\n\n"
        f"<b>Команды:</b>\n"
        f"/birthdays — все дни рождения по порядку\n"
        f"/next — кто следующий именинник\n"
        f"/today — есть ли сегодня именинники\n"
        f"/week — дни рождения на ближайшую неделю\n"
        f"/open — открыть страницу с днями рождения"
    )

def is_auth(update: Update) -> bool:
    return update.effective_chat.id in authorized_users

# ══════════════════════════════════════════
#  КОМАНДЫ
# ══════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    waiting_password.add(chat_id)
    await update.message.reply_text(
        f"🔐 Добро пожаловать!\n\n"
        f"Это бот группы <b>{GROUP_NAME}</b>.\n"
        f"Введите пароль группы чтобы продолжить:",
        parse_mode="HTML"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    # Ждём пароль
    if chat_id in waiting_password:
        if text == PASSWORD:
            waiting_password.discard(chat_id)
            authorized_users.add(chat_id)
            keyboard = [[InlineKeyboardButton(
                "🎂 Открыть дни рождения",
                url=MINIAPP_URL
            )]]
            await update.message.reply_text(
                welcome_text(),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                "❌ Неверный пароль. Попробуйте ещё раз:"
            )
        return

    # Не авторизован
    if chat_id not in authorized_users:
        await update.message.reply_text(
            "🔐 Введите /start чтобы авторизоваться."
        )

async def cmd_birthdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update):
        await update.message.reply_text("🔐 Введите /start чтобы авторизоваться."); return
    sorted_bdays = sorted(BIRTHDAYS, key=lambda x: days_until(x[2], x[3]))
    lines = []
    for nik, name, month, day, g in sorted_bdays:
        diff = days_until(month, day)
        emoji = "🎂" if diff == 0 else "🎉" if diff <= 7 else "📅"
        lines.append(f"{emoji} {name} {nik} — {day} {MONTH_NAMES[month]} ({format_days(diff)})")
    await update.message.reply_text(
        f"🎂 <b>Все дни рождения {GROUP_NAME}:</b>\n\n" + "\n".join(lines),
        parse_mode="HTML"
    )

async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update):
        await update.message.reply_text("🔐 Введите /start чтобы авторизоваться."); return
    sorted_bdays = sorted(BIRTHDAYS, key=lambda x: days_until(x[2], x[3]))
    nik, name, month, day, g = sorted_bdays[0]
    diff = days_until(month, day)
    if diff == 0:
        text = f"🎂 <b>Сегодня!</b> День рождения у {nik} — {name}! 🥳"
    elif diff == 1:
        text = f"🎉 <b>Уже завтра!</b> День рождения у {nik} — {name} ({day} {MONTH_NAMES[month]})"
    else:
        text = f"📅 <b>Следующий именинник:</b>\n\n{name} {nik}\n🗓 {day} {MONTH_NAMES[month]} — {format_days(diff)}"
    await update.message.reply_text(text, parse_mode="HTML")

async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update):
        await update.message.reply_text("🔐 Введите /start чтобы авторизоваться."); return
    todays = [(nik, name, m, d, g) for nik, name, m, d, g in BIRTHDAYS if days_until(m, d) == 0]
    if not todays:
        await update.message.reply_text("😊 Сегодня именинников нет. Используй /next чтобы узнать кто следующий.")
    else:
        lines = [f"🎂 {name} {nik}" for nik, name, m, d, g in todays]
        await update.message.reply_text(
            "🥳 <b>Сегодня день рождения у:</b>\n\n" + "\n".join(lines) + "\n\nНе забудьте поздравить! 🎉",
            parse_mode="HTML"
        )

async def cmd_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update):
        await update.message.reply_text("🔐 Введите /start чтобы авторизоваться."); return
    week = sorted(
        [(nik, name, m, d, g) for nik, name, m, d, g in BIRTHDAYS if days_until(m, d) <= 7],
        key=lambda x: days_until(x[2], x[3])
    )
    if not week:
        await update.message.reply_text("😊 В ближайшие 7 дней именинников нет. Используй /next.")
    else:
        lines = []
        for nik, name, m, d, g in week:
            diff = days_until(m, d)
            emoji = "🎂" if diff == 0 else "🎉"
            lines.append(f"{emoji} {name} {nik} — {d} {MONTH_NAMES[m]} ({format_days(diff)})")
        await update.message.reply_text(
            "📅 <b>Дни рождения на ближайшую неделю:</b>\n\n" + "\n".join(lines),
            parse_mode="HTML"
        )

async def cmd_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update):
        await update.message.reply_text("🔐 Введите /start чтобы авторизоваться."); return
    keyboard = [[InlineKeyboardButton("🎂 Открыть дни рождения", url=MINIAPP_URL)]]
    await update.message.reply_text(
        "👇 Нажми чтобы открыть страницу с днями рождения:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ══════════════════════════════════════════
#  НАПОМИНАНИЯ В ЛИЧКУ
# ══════════════════════════════════════════
async def send_personal_reminders(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in list(authorized_users):
        messages = []
        for nik, name, month, day, g in BIRTHDAYS:
            diff = days_until(month, day)
            if diff == 1:
                messages.append(
                    f"⏰ <b>Завтра день рождения!</b>\n\n"
                    f"Не забудь поздравить {nik} — {name}! 🎁"
                )
            elif diff == 3:
                messages.append(
                    f"📅 <b>Через 3 дня день рождения!</b>\n\n"
                    f"У {name} {nik} праздник {day} {MONTH_NAMES[month]}.\n"
                    f"Самое время придумать поздравление! 🎉"
                )
        for msg in messages:
            try:
                await context.bot.send_message(
                    chat_id=chat_id, text=msg, parse_mode="HTML"
                )
            except Exception as e:
                print(f"Ошибка отправки {chat_id}: {e}")
                authorized_users.discard(chat_id)

# ══════════════════════════════════════════
#  ЗАПУСК
# ══════════════════════════════════════════
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("help",      cmd_start))
    app.add_handler(CommandHandler("birthdays", cmd_birthdays))
    app.add_handler(CommandHandler("next",      cmd_next))
    app.add_handler(CommandHandler("today",     cmd_today))
    app.add_handler(CommandHandler("week",      cmd_week))
    app.add_handler(CommandHandler("open",      cmd_open))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Напоминания каждый день в 9:00 МСК
    run_time = datetime.time(
        hour=9, minute=0,
        tzinfo=datetime.timezone(datetime.timedelta(hours=3))
    )
    app.job_queue.run_daily(send_personal_reminders, time=run_time)

    print(f"Бот {GROUP_NAME} запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
