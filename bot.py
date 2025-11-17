
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS_FILE = Path("chat_ids.json")


def load_chat_ids():
    if CHAT_IDS_FILE.exists():
        try:
            return json.loads(CHAT_IDS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_chat_ids(chat_ids):
    CHAT_IDS_FILE.write_text(json.dumps(chat_ids, indent=2), encoding="utf-8")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    chat_ids = load_chat_ids()
    if chat_id not in chat_ids:
        chat_ids.append(chat_id)
        save_chat_ids(chat_ids)
        msg = "✅ Siz muvaffaqiyatli roʻyxatdan oʻtdingiz. Endi Upwork, GitHub va boshqa manbalardan keladigan zakazlar haqida Telegram orqali xabar olasiz."
    else:
        msg = "Siz allaqachon roʻyxatdan oʻtgansiz. Yangi zakazlar boʻyicha xabarlar shu chatga keladi."
    await update.message.reply_text(msg)


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_ids = load_chat_ids()
    if chat_id in chat_ids:
        await update.message.reply_text("✅ Siz tizimga ulanganingiz. Xabarlar shu yerga keladi.")
    else:
        await update.message.reply_text("❌ Siz hali roʻyxatdan oʻtmagansiz. /start buyrugʻini bosing.")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Bu bot sizga quyidagilar boʻyicha bildirishnoma yuboradi:\n"
        "• Upwork takliflari, invaytlar, xabarlar (email orqali)\n"
        "• GitHubda yangi issue, PR, mention va h.k.\n"
        "• Boshqa saytlar – email orqali filtrlangan xabarlar\n\n"
        "Boshlash uchun: /start\n"
        "Holatni tekshirish: /status"
    )
    await update.message.reply_text(text)


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN .env faylida ko'rsatilmagan")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("help", help_cmd))

    logger.info("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
