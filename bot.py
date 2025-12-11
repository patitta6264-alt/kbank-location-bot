import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# โหลดข้อมูลจากไฟล์ Excel (data.xlsx ต้องอยู่ใน repository)
df = pd.read_excel("data.xlsx")

async def reply_cid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.text.strip()

    # ค้นหา row ตามคอลัมน์ "CID"
    rows = df[df["CID"] == cid]

    if rows.empty:
        await update.message.reply_text("❌ ไม่พบข้อมูล CID นี้ค่ะ")
        return

    row = rows.iloc[0]

    # ปรับชื่อคอลัมน์ตามไฟล์จริง (ตัวอย่าง: 'ปลายทาง', 'Lat', 'Long')
    dest = row.get("ปลายทาง", "ไม่ระบุ")
    # บางไฟล์ชื่อคอลัมน์อาจต่างกัน (เช่น 'lat' / 'LAT') — ตรวจสอบให้ตรง
    lat = row.get("Lat") if "Lat" in row.index else row.get("lat") if "lat" in row.index else row.get("LAT")
    lon = row.get("Long") if "Long" in row.index else row.get("long") if "long" in row.index else row.get("LONG")

    # ถ้า lat/long เป็น NaN หรือ None ให้แจ้งกลับ
    if pd.isna(lat) or pd.isna(lon):
        await update.message.reply_text("❌ พิกัดไม่ถูกต้องในข้อมูล")
        return

    maps_url = f"https://www.google.com/maps?q={lat},{lon}"

    reply_msg = (
        f"📍 ข้อมูลลูกค้า\n"
        f"CID: {cid}\n"
        f"ปลายทาง: {dest}\n"
        f"Lat: {lat}\n"
        f"Long: {lon}\n"
        f"📌 เปิด Maps:\n{maps_url}"
    )

    await update.message.reply_text(reply_msg)
    # ส่ง location เป็นแผนที่ด้วย
    await update.message.reply_location(latitude=float(lat), longitude=float(lon))


if __name__ == "__main__":
    # อ่าน token จาก Environment Variable ชื่อ BOT_TOKEN
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise SystemExit("ERROR: BOT_TOKEN environment variable not set")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_cid))

    # รันแบบ polling (เหมาะกับ Render)
    app.run_polling()
