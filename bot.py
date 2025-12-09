import os
import logging
import pandas as pd
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ตั้ง logging เพื่อดู error ที่ชัดเจนใน log ของ Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# โหลด token จาก environment (ต้องตั้งชื่อเป็น BOT_TOKEN บน Render)
TOKEN = os.getenv("8324571927:AAHINhNwQZxb8e5VVzl2kEt-RbHUP_Bh610")
if not TOKEN:
    logger.error("BOT_TOKEN environment variable not set!")
    raise SystemExit("BOT_TOKEN environment variable not set")

# ชื่อไฟล์ Excel (ต้องอยู่ใน repo เดียวกับ bot.py หรือ path ถูกต้อง)
DATA_FILE = "data.xlsx"

# โหลด DataFrame ตอนเริ่ม ถ้าไฟล์หาไม่เจอจะออก error ให้เห็นใน log
try:
    df = pd.read_excel(DATA_FILE)
    # ทำให้คอลัมน์ CID เป็น string เพื่อเทียบง่าย
    df["CID"] = df["CID"].astype(str)
    logger.info("Loaded data.xlsx with %d rows", len(df))
except Exception as e:
    logger.exception("Cannot load data file '%s': %s", DATA_FILE, e)
    raise

def find_cid(cid_value: str):
    # เปรียบเทียบแบบไม่ sensitive ตัวพิมพ์-เล็ก (upper)
    try:
        matched = df[df["CID"].str.upper() == cid_value.strip().upper()]
    except Exception as e:
        logger.exception("Error searching CID: %s", e)
        return None

    if matched.empty:
        return None

    row = matched.iloc[0]

    # เปลี่ยนชื่อตามคอลัมน์ใน Excel ของคุณ (เช่น 'Location','LAT','Long','Due Date')
    location = row.get("Location", "")
    due = row.get("Due Date", "")
    lat = row.get("LAT", "")
    long = row.get("Long", "")

    text = (
        f"✅ พบข้อมูล\nCID: {cid_value}\n"
        f"ปลายทาง: {location}\n"
        f"Due Date: {due}\n"
        f"LAT: {lat}\nLONG: {long}"
    )
    return text

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("สวัสดี! ส่ง CID มาให้หน่อย เช่น VPNKBG1911")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ส่งรหัส CID มาเพื่อค้นหาพิกัดจากไฟล์ Excel ค่ะ")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    # ถ้าอยากให้รับคำสั่งแบบ / จะละไว้ — ที่นี่เป็นรับข้อความธรรมดา
    logger.info("Received message: %s", text)
    result = find_cid(text)
    if result:
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("❌ ไม่พบข้อมูลสำหรับ CID นี้")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("Starting bot (polling)...")
    app.run_polling()

if __name__ == "__main__":
    main()
