# bot.py - KBank Location Bot (PTB v20)
# การใช้งาน:
# 1) วาง bot.py ไว้ในโฟลเดอร์เดียวกับ data.xlsx
# 2) แก้ TOKEN ให้เป็นของบอทคุณ
# 3) ติดตั้งไลบรารี: python -m pip install python-telegram-bot==20 pandas openpyxl
# 4) รัน: python bot.py

import sys
import asyncio
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# ---- สำหรับ Windows: พยายามตั้ง event loop policy (ป้องกัน issue บางเครื่อง) ----
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

# ---------- ตั้งชื่อไฟล์ Excel ที่จะอ่าน ----------
EXCEL_FILE = "data.xlsx"

def load_data(path: str) -> pd.DataFrame:
    """
    โหลด Excel เป็น DataFrame และตรวจคอลัมน์สำคัญ
    """
    try:
        df = pd.read_excel(path)
        # ตรวจว่าอย่างน้อยมีคอลัมน์ CID และ ปลายทาง
        if "CID" not in df.columns or "ปลายทาง" not in df.columns:
            print("ERROR: data.xlsx ต้องมีคอลัมน์ 'CID' และ 'ปลายทาง' (ตรวจสอบชื่อคอลัมน์)")
            return pd.DataFrame()
        return df
    except FileNotFoundError:
        print(f"ERROR: ไม่พบไฟล์ {path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERROR loading {path}: {e}")
        return pd.DataFrame()

# โหลดข้อมูลครั้งแรก
DF = load_data(EXCEL_FILE)

# ---- คำสั่ง /start เพื่อทดสอบว่า bot ทำงาน ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("สวัสดี! ส่ง CID (เช่น VPNKBG1911) มาให้บอทเพื่อตรวจสอบตำแหน่งได้เลย")

# ฟังก์ชันช่วยตัดข้อความปลายทางให้เริ่มจากคำว่า 'ATM' (ถ้ามี)
def extract_from_atm(full_text: str) -> str:
    if not full_text:
        return ""
    lower = full_text.lower()
    pos = lower.find("atm")
    if pos != -1:
        return full_text[pos:].strip()
    return full_text.strip()

# ฟังก์ชันหลัก: รับ CID แล้วตอบกลับข้อมูล + พิกัด/ลิงก์
async def reply_cid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DF
    text = (update.message.text or "").strip()
    cid = text

    if DF.empty:
        await update.message.reply_text("❗ ข้อมูลไม่พร้อมใช้งาน (data.xlsx)")
        return

    # ค้นหา CID แบบตรงตัว (strip) — ปรับเป็น .upper() ถ้าต้องการ ignore case
    mask = DF["CID"].astype(str).str.strip() == cid
    result = DF[mask]

    if result.empty:
        await update.message.reply_text("❌ ไม่พบ CID ในระบบ")
        return

    row = result.iloc[0]

    # อ่านปลายทางและตัดข้อความตั้งแต่ 'ATM' ถ้ามี
    full_dest = str(row.get("ปลายทาง", "")).strip()
    dest = extract_from_atm(full_dest)

    # อ่านพิกัดจากคอลัมน์ตามไฟล์ของคุณ (กำหนดเป็น LAT และ Long)
    lat = None
    lon = None
    try:
        # บางแถวอาจเป็น NaN -> ใช้ try/except
        if "LAT" in row.index and pd.notna(row["LAT"]):
            lat = float(row["LAT"])
        if "Long" in row.index and pd.notna(row["Long"]):
            lon = float(row["Long"])
    except Exception:
        lat = None
        lon = None

    # สร้างข้อความตอบ
    reply_lines = [
        "✅ พบข้อมูล",
        f"CID: {cid}",
        f"ปลายทาง: {dest if dest else full_dest if full_dest else '-'}"
    ]

    # ถ้ามีพิกัด ให้ส่ง location (หมุด) และแนบลิงก์ Google Maps
    if lat is not None and lon is not None:
        # ส่งหมุด location
        try:
            await update.message.reply_location(latitude=lat, longitude=lon)
        except Exception:
            # ถ้ามีปัญหาการส่ง location ให้ดำเนินต่อไปส่งลิงก์แทน
            pass

        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        reply_lines.append(f"พิกัด: {lat}, {lon}")
        reply_lines.append(f"เปิด Maps: {maps_url}")
    else:
        reply_lines.append("พิกัด: ไม่พบ")

    await update.message.reply_text("\n".join(reply_lines))

# ---------- TOKEN ของบอท: ใส่ของคุณตรงนี้หรืออ่านจาก environment ----------
TOKEN = "8324571927:AAHINhNwQZxb8e5VVzl2kEt-RbHUP_Bh610"

# ---------- สร้าง Application และเพิ่ม handler ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_cid))

    # สร้าง event loop ใหม่ แล้วตั้งเป็นปัจจุบัน (ป้องกันปัญหา Windows บางรุ่น)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    print("Starting bot... (กด Ctrl+C เพื่อหยุด)")
    app.run_polling()

if __name__ == "__main__":
    main()