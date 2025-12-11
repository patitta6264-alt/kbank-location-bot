import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import os

async def reply_cid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # โหลดไฟล์ Excel
    df = pd.read_excel("data.xlsx")

    # หาแถวที่ CID ตรงกับข้อความที่ส่งมา
    row = df[df["CID"] == text]

    if row.empty:
        await update.message.reply_text("ไม่พบข้อมูลค่ะ")
        return

    cid = row["CID"].values[0]
    dest = row["Destination"].values[0]
    lat = row["Lat"].values[0]
    lon = row["Lon"].values[0]

    maps_url = f"https://www.google.com/maps?q={lat},{lon}"

    reply_msg = (
        f"ข้อมูลที่พบค่ะ\n"
        f"CID: {cid}\n"
        f"ปลายทาง: {dest}\n"
        f"Lat: {lat}\n"
        f"Lon: {lon}\n"
        f"ดูแผนที่: {maps_url}"
    )

    await update.message.reply_text(reply_msg)
    await update.message.reply_location(latitude=lat, longitude=lon)


TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, reply_cid))

app.run_polling()
