import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# โหลดข้อมูล Excel
df = pd.read_excel("data.xlsx")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("พิมพ์ชื่อธนาคารหรือสาขาที่ต้องการค้นหาได้เลยค่ะ")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    result = df[df["branch"].str.contains(query, case=False, na=False)]

    if result.empty:
        await update.message.reply_text("ไม่พบข้อมูลค่ะ")
        return

    reply = ""
    for _, row in result.iterrows():
        reply += f"🏦 {row['bank']} - {row['branch']}\n📍 {row['location']}\n\n"

    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("", search))  # พิมพ์อะไรก็ค้นหา

    print("BOT STARTED...")
    app.run_polling()

if __name__ == "__main__":
    main()
