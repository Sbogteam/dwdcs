from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8337826639:AAHD-mDNgGanhZeV79BQ--6_Su2Sc6u557M"

# Главное меню при /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👋 Привет! Меня зовут Моника.\n\n🎥 Здесь я продаю доступ к приватному каналу.\n\nВыбери тип подписки 👇"
    keyboard = [
        [InlineKeyboardButton("Приват", callback_data="type_private"), InlineKeyboardButton("Приват +", callback_data="type_private_plus")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# Обработка выбора типа приват
async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "type_private":
        text = (
            "💼 *Приват*\n"
            "– Доступ к старым видео, которые скидываются из Приват +\n\n"
            "Выбери срок подписки и цену:"
        )
        keyboard = [
            [InlineKeyboardButton("1 месяц – 1500 ₽", callback_data="buy_private_1m")],
            [InlineKeyboardButton("6 месяцев – 2500 ₽", callback_data="buy_private_6m")],
            [InlineKeyboardButton("1 год – 4000 ₽", callback_data="buy_private_1y")],
            [InlineKeyboardButton("Навсегда – 6000 ₽", callback_data="buy_private_forever")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_start")]
        ]
    else:  # type_private_plus
        text = (
            "💎 *Приват +*\n"
            "– Все новые видео, снятые в течение месяца и регулярно пополняемые\n\n"
            "Выбери срок подписки и цену:"
        )
        keyboard = [
            [InlineKeyboardButton("1 месяц – 2500 ₽", callback_data="buy_private_plus_1m")],
            [InlineKeyboardButton("6 месяцев – 3500 ₽", callback_data="buy_private_plus_6m")],
            [InlineKeyboardButton("1 год – 6000 ₽", callback_data="buy_private_plus_1y")],
            [InlineKeyboardButton("Навсегда – 8000 ₽", callback_data="buy_private_plus_forever")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_start")]
        ]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Обработка выбора покупки тарифов
async def buy_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plans = {
        "buy_private_1m": ("Приват на 1 месяц", "1500 ₽"),
        "buy_private_6m": ("Приват на 6 месяцев", "2500 ₽"),
        "buy_private_1y": ("Приват на 1 год", "4000 ₽"),
        "buy_private_forever": ("Приват навсегда", "6000 ₽"),
        "buy_private_plus_1m": ("Приват + на 1 месяц", "2500 ₽"),
        "buy_private_plus_6m": ("Приват + на 6 месяцев", "3500 ₽"),
        "buy_private_plus_1y": ("Приват + на 1 год", "6000 ₽"),
           await query.edit_message_text("❌ Ошибка выбора. Попробуйте ещё раз.")
        return

    text = (
        f"💳 Вы выбрали: *{plan_name}*\n"
        f"💰 Цена: *{price}*\n\n"
        "Номер для оплаты:\n"
        "📲 `2202208324636159`\n\n"
        "После оплаты нажмите кнопку ниже и прикрепите чек (фото или PDF).\n\n"
        "📄 *Формат чека*: PNG, JPG, PDF"
    )
    keyboard = [[InlineKeyboardButton("Прикрепить чек", callback_data="attach_receipt")]]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    # Сохраняем для пользователя, что он сейчас отправляет чек (на случай дальнейшей обработки)
    context.user_data["awaiting_receipt"] = True
    context.user_data["selected_plan"] = plan_name

# Обработка прикрепления чека (в данном примере просто подтверждаем)
async def attach_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📤 Пожалуйста, отправьте файл с чеком в этом чате.")

    context.user_data["receipt_requested"] = True

# Обработка получения файла с чеком
async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("receipt_requested"):
        return  # Игнорируем если чек не ожидается

    # Проверяем, что пришёл нужный тип файла: фото, документ с нужным расширением
    if update.message.photo or (update.message.document and update.message.document.mime_type in ["application/pdf", "image/png", "image/jpeg"]):
        plan = context.user_data.get("selected_plan", "ваш план")
        await update.message.reply_text(
            f"✅ Спасибо за покупку *{plan}*! \n\n"
            "⏳ Ожидайте ссылку на вход в течение короткого времени.\n\n"
            "Если будут вопросы — напишите мне.",
            parse_mode="Markdown"
        )
        # Очистка состояния
        context.user_data.clear()
    else:
        await update.message.reply_text(
            "⚠️ Пожалуйста, отправьте файл в формате PNG, JPG или PDF."
        )

# Обработка кнопки назад
async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_type, pattern="^(type_private|type_private_plus)$"))
    app.add_handler(CallbackQueryHandler(buy_plan, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(attach_receipt, pattern="attach_receipt"))
    app.add_handler(CallbackQueryHandler(back_to_start, pattern="back_to_start"))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO & filters.TEXT & (~filters.COMMAND), receive_receipt))

    print("Бот запущен...")
    app.run_polling()     "buy_private_plus_forever": ("Приват + навсегда", "8000 ₽"),
    }

    plan_name, price = plans.get(query.data, (None, None))
    if not plan_name:
