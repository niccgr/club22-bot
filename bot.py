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
CHECK_HOUR = 9   # час отправки автонапоминаний (МСК, UTC+3)

# ══════════════════════════════════════════
#  СПИСОК ДР: (ник, имя, месяц, день, пол)
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
            msg = (
                f"🎂 <b>Сегодня день рождения!</b>\n\n"
                f"Поздравляем {nik} — {name}! 🎉\n"
                f"Пусть этот день будет особенным, "
                f"{gender(g, 'дорогой', 'дорогая')} {name}! 🥳"
            )
            messages.append(msg)

        elif diff == 3:
            msg = (
                f"⏰ <b>Через 3 дня — день рождения {nik}!</b>\n\n"
                f"У {name} праздник {day} {MONTH_NAMES[month]}.\n"
                f"Самое время придумать поздравление! 🎁"
            )
            messages.append(msg)

        elif diff == 7:
            msg = (
                f"📅 <b>Через неделю день рождения {nik}!</b>\n\n"
                f"{name} {gender(g, 'отмечает', 'отмечает')} день рождения "
                f"{day} {MONTH_NAMES[month]}.\n"
                f"Не забудьте поздравить! 🌟"
            )
            messages.append(msg)

    if messages:
        for msg in messages:
            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
            await asyncio.sleep(1)
        print(f"[{today}] Отправлено {len(messages)} напоминаний")
    else:
        print(f"[{today}] Нет напоминаний на сегодня")

# ══════════════════════════════════════════
#  КОМАНДЫ
# ══════════════════════════════════════════

# /start или /help
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 <b>Привет! Я бот Клуба 22.</b>\n\n"
        "Слежу за днями рождения и напоминаю вовремя.\n\n"
        "<b>Команды:</b>\n"
        "/birthdays — все дни рождения по порядку\n"
        "/next — кто следующий именинник\n"
        "/today — есть ли сегодня именинники\n"
        "/week — дни рождения в ближайшие 7 дней"
    )
    await update.message.reply_text(text, parse_mode="HTML")

# /birthdays — полный список
async def cmd_birthdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_bdays = sorted(BIRTHDAYS, key=lambda x: days_until(x[2], x[3]))
    lines = []
    for nik, name, month, day, g in sorted_bdays:
        diff = days_until(month, day)
        emoji = "🎂" if diff == 0 else "🎉" if diff <= 7 else "📅"
        lines.append(f"{emoji} {name} {nik} — {day} {MONTH_NAMES[month]} ({format_days(diff)})")

    text = "🎂 <b>Все дни рождения Клуба 22:</b>\n\n" + "\n".join(lines)
    await update.message.reply_text(text, parse_mode="HTML")

# /next — следующий именинник
async def cmd_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_bdays = sorted(BIRTHDAYS, key=lambda x: days_until(x[2], x[3]))
    nik, name, month, day, g = sorted_bdays[0]
    diff = days_until(month, day)

    if diff == 0:
        text = f"🎂 <b>Сегодня!</b> День рождения у {nik} — {name}! 🥳"
    elif diff == 1:
        text = f"🎉 <b>Уже завтра!</b> День рождения у {nik} — {name} ({day} {MONTH_NAMES[month]})"
    else:
        text = (
            f"📅 <b>Следующий именинник:</b>\n\n"
            f"{name} {nik}\n"
            f"🗓 {day} {MONTH_NAMES[month]} — {format_days(diff)}"
        )
    await update.message.reply_text(text, parse_mode="HTML")

# /today — именинники сегодня
async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    todays = [(nik, name, m, d, g) for nik, name, m, d, g in BIRTHDAYS if days_until(m, d) == 0]
    if not todays:
        await update.message.reply_text("😊 Сегодня именинников нет. Следующий день рождения скоро — используй /next")
    else:
        lines = [f"🎂 {name} {nik}" for nik, name, m, d, g in todays]
        text = "🥳 <b>Сегодня день рождения у:</b>\n\n" + "\n".join(lines) + "\n\nНе забудьте поздравить! 🎉"
        await update.message.reply_text(text, parse_mode="HTML")

# /week — ближайшие 7 дней
async def cmd_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    week = [(nik, name, m, d, g) for nik, name, m, d, g in BIRTHDAYS if days_until(m, d) <= 7]
    week.sort(key=lambda x: days_until(x[2], x[3]))

    if not week:
        await update.message.reply_text("😊 В ближайшие 7 дней именинников нет. Используй /next чтобы узнать кто следующий.")
    else:
        lines = []
        for nik, name, m, d, g in week:
            diff = days_until(m, d)
            emoji = "🎂" if diff == 0 else "🎉"
            lines.append(f"{emoji} {name} {nik} — {d} {MONTH_NAMES[m]} ({format_days(diff)})")
        text = "📅 <b>Дни рождения на ближайшую неделю:</b>\n\n" + "\n".join(lines)
        await update.message.reply_text(text, parse_mode="HTML")

# ══════════════════════════════════════════
#  ФОНОВАЯ ЗАДАЧА — авто-напоминания
# ══════════════════════════════════════════
async def scheduler(bot: Bot):
    print(f"Планировщик запущен. Напоминания в {CHECK_HOUR}:00 МСК каждый день.")
    sent_today = False
    while True:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        if now.hour == CHECK_HOUR and now.minute < 1:
            if not sent_today:
                await send_reminders(bot)
                sent_today = True
        else:
            sent_today = False
        await asyncio.sleep(30)

# ══════════════════════════════════════════
#  ЗАПУСК
# ══════════════════════════════════════════
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем команды
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_start))
    app.add_handler(CommandHandler("birthdays", cmd_birthdays))
    app.add_handler(CommandHandler("next",  cmd_next))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("week",  cmd_week))

    # Устанавливаем меню команд у бота
    await app.bot.set_my_commands([
        BotCommand("birthdays", "Все дни рождения по порядку"),
        BotCommand("next",      "Следующий именинник"),
        BotCommand("today",     "Есть ли сегодня именинники"),
        BotCommand("week",      "Дни рождения на ближайшую неделю"),
        BotCommand("help",      "Помощь"),
    ])

    print("Бот запущен!")

    # Запускаем планировщик параллельно
    asyncio.create_task(scheduler(app.bot))

    await app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())
