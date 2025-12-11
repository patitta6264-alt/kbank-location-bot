import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# โหลดข้อมูล
df = pd.read_excel("data.xlsx")

async def reply_cid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.text.strip()

    if not cid.isdigit():
        await update.message.reply_text("❌ กรุณาพิมพ์เฉพาะตัวเลข CID")
        return

    row = df[df["CID"] == int(cid)]

    if row.empty:
        await update.message.reply_text("❌ ไม่พบข้อมูลลูกค้า")
        return

    data = row.iloc[0]

    dest = data["ปลายทาง"]
    lat = data["Lat"]
    lon = data["Long"]

    maps_url = f"https://www.google.com/maps?q={lat},{lon}"

    reply_msg = (
        f"📍 ข้อมูลลูกค้า\n"
        f"CID: {cid}\n"
        f"ปลายทาง: {dest}\n"
        f"Lat: {lat}\n"
        f"Long: {lon}\n\n"
        f"📌 เปิด Maps: {maps_url}"
    )

    await update.message.reply_text(reply_msg)
    await update.message.reply_location(latitude=lat, longitude=lon)

# อ่าน TOKEN จาก environment variables
import os
TOKEN = os.environ.get("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, reply_cid))

if __name__ == "__main__":
    app.run_polling()
