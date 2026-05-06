import asyncio
import datetime
from telegram import Bot, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from telegram.error import TelegramError

# ══════════════════════════════════════════
#  НАСТРОЙКИ
# ══════════════════════════════════════════
BOT_TOKEN  = "8686292524:AAHMoMyW8gwnD_JkcZrOEObq3HL13KAZtM4"
CHAT_ID    = -1001490833744
CHECK_HOUR = 9   # час отправки (МСК, UTC+3)

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

# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════
def days_until(month, day):
    today = datetime.date.today()
    next_bd = datetime.date(today.year, month, day)
    if next_bd < today:
        next_bd = datetime.date(today.year + 1, month, day)
    return (next_bd - today).days

def gender(g, male, female):
    return female if g == "f" else male

def format_days(n):
    if n == 0: return "сегодня 🎂"
    if n == 1: return "завтра"
    if 2 <= n <= 4: return f"через {n} дня"
    return f"через {n} дней"

# ══════════════════════════════════════════
#  АВТО-НАПОМИНАНИЯ
# ══════════════════════════════════════════
async def send_reminders(bot: Bot):
    today = datetime.date.today()
    messages = []

    for nik, name, month, day, g in BIRTHDAYS:
        diff = days_until(month, day)

        if diff == 0:
            messages.append(
                f"🎂 <b>Сегодня день рождения!</b>\n\n"
                f"Поздравляем {nik} — {name}! 🎉\n"
                f"Пусть этот день будет особенным, "
                f"{gender(g, 'дорогой', 'дорогая')} {name}! 🥳"
            )
        elif diff == 3:
            messages.append(
                f"⏰ <b>Через 3 дня — день рождения {nik}!</b>\n\n"
                f"У {name} праздник {day} {MONTH_NAMES[month]}.\n"
                f"Самое время придумать поздравление! 🎁"
            )
        elif diff == 7:
            messages.append(
                f"📅 <b>Через неделю день рождения {nik}!</b>\n\n"
                f"{name} отмечает день рождения {day} {MONTH_NAMES[month]}.\n"
                f"Не забудьте поздравить! 🌟"
            )

    for msg in messages:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
            await asyncio.sleep(1)
        except TelegramError as e:
            print(f"Ошибка отправки: {e}")

    print(f"[{today}] Напоминаний отправлено: {len(messages)}")

# ══════════════════════════════════════════
#  КОМАНДЫ
# ══════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>Привет! Я бот Клуба 22.</b>\n\n"
        "Слежу за днями рождения и напоминаю вовремя.\n\n"
        "<b>Команды:</b>\n"
        "/birthdays — все дни рождения по порядку\n"
        "/next — кто следующий именинник\n"
        "/today — есть ли сегодня именинники\n"
        "/week — дни рождения в ближайшие 7 дней",
        parse_mode="HTML"
    )

async def cmd_birthdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_bdays = sorted(BIRTHDAYS, key=lambda x: days_until(x[2], x[3]))
    lines = []
    for nik, name, month, day, g in sorted_bdays:
        diff = days_until(month, day)
        emoji = "🎂" if diff == 0 else "🎉" if diff <= 7 else "📅"
        lines.append(f"{emoji} {name} {nik} — {day} {MONTH_NAMES[month]} ({format_days(diff)})")
    await update.message.reply_text(
        "🎂 <b>Все дни рождения Клуба 22:</b>\n\n" + "\n".join(lines),
        parse_mode="HTML"
    )

async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# ══════════════════════════════════════════
#  ПЛАНИРОВЩИК — через job_queue
# ══════════════════════════════════════════
async def scheduler_job(context: ContextTypes.DEFAULT_TYPE):
    await send_reminders(context.bot)

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

    # Запускаем планировщик через встроенный job_queue
    # Каждый день в CHECK_HOUR:00 по МСК (UTC+3)
    run_time = datetime.time(
        hour=CHECK_HOUR,
        minute=0,
        tzinfo=datetime.timezone(datetime.timedelta(hours=3))
    )
    app.job_queue.run_daily(scheduler_job, time=run_time)

    print("Бот запущен! Напоминания каждый день в", CHECK_HOUR, ":00 МСК")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
