import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd

TOKEN = os.getenv("BOT_TOKEN")
df = pd.read_excel("data.xlsx")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("สวัสดี! พิมพ์คำค้นเพื่อหาสาขาได้เลย")

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("ใส่คำค้นก่อนค่ะ")
        return
    res = df[df.apply(lambda r: text.lower() in str(r.astype(str)).lower(), axis=1)]
    if res.empty:
        await update.message.reply_text("ไม่พบข้อมูล")
        return
    reply = ""
    for _, row in res.iterrows():
        reply += f"{row.get('branch','')} | {row.get('location','')}\n"
    await update.message.reply_text(reply)

def main():
    if not TOKEN:
        raise SystemExit("BOT_TOKEN environment variable not set")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
