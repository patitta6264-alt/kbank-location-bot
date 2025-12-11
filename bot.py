from telegram.ext import ApplicationBuilder, MessageHandler, filters

async def reply_cid(update, context):
    text = update.message.text.strip()

    # แยกข้อมูล
    try:
        cid, dest, lat, lon = text.split(",")
    except:
        await update.message.reply_text("❌ รูปแบบข้อมูลไม่ถูกต้อง\nตัวอย่าง: 1001,ATM,7.1234,100.5678")
        return

    maps_url = f"https://www.google.com/maps?q={lat},{lon}"

    reply_msg = (
        f"📌 ข้อมูลลูกค้า\n"
        f"CID: {cid}\n"
        f"ปลายทาง: {dest}\n"
        f"Lat: {lat}\n"
        f"Long: {lon}\n"
        f"➡️ เปิด Maps: {maps_url}"
    )

    await update.message.reply_text(reply_msg)
    await update.message.reply_location(latitude=float(lat), longitude=float(lon))


# ------------------------
# Main function
# ------------------------
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_cid))

app.run_polling()
