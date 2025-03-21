import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

LANGUAGES = {
    'fa-de': 'فارسی → آلمانی',
    'de-fa': 'آلمانی → فارسی',
    'en-de': 'انگلیسی → آلمانی',
    'de-en': 'آلمانی → انگلیسی',
    'ru-de': 'روسی → آلمانی',
    'de-ru': 'آلمانی → روسی'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(LANGUAGES[key], callback_data=key)] for key in LANGUAGES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('🌍 لطفاً زبان ترجمه را انتخاب کنید:', reply_markup=reply_markup)

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['lang_pair'] = query.data
    await query.edit_message_text(text=f"✅ زبان انتخاب‌شده: {LANGUAGES[query.data]}\n\n📝 حالا یک کلمه برای ترجمه ارسال کن:")

async def translate_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_pair = context.user_data.get('lang_pair')
    if not lang_pair:
        await update.message.reply_text("لطفاً اول با /start زبان رو انتخاب کن.")
        return

    word = update.message.text.strip()
    src_lang, tgt_lang = lang_pair.split('-')
    url = f"https://glosbe.com/gapi/translate?from={src_lang}&dest={tgt_lang}&format=json&phrase={word}&pretty=true"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        tuc = data.get('tuc', [])
        if tuc and 'phrase' in tuc[0]:
            translation = tuc[0]['phrase']['text']
            example = data.get('examples', [{}])[0].get('first', 'مثالی در دسترس نیست.')
            await update.message.reply_text(
                f"📌 ترجمه: {translation}\n📖 مثال: {example}"
            )
        else:
            await update.message.reply_text("😕 ترجمه‌ای پیدا نشد. لطفاً کلمه‌ای دیگر امتحان کن.")
    else:
        await update.message.reply_text("⚠️ خطا در ارتباط با Glosbe.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(select_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_word))

    print("✅ ربات در حال اجراست...")
    app.run_polling()
