
import logging
import asyncio
import socket
import aiohttp
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = "7616386838:AAGAJeWB0Z4OG1PMshVIrcEpwXD8yaOj0S0"
IPQS_API_KEY = "ZLsvHEr0d0MWIo3E4vDivecwUjeLKl0s"

proxy_list = [
    # Apne proxies yahan daal sakte ho
    "127.0.0.1:1080",
    "192.168.1.1:1080",
    "8.8.8.8:1080",
    # ...
]

async def is_proxy_alive(ip: str, port: int, timeout=3):
    try:
        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(
            None, lambda: socket.create_connection((ip, port), timeout)
        )
        conn = await asyncio.wait_for(fut, timeout=timeout)
        conn.close()
        return True
    except Exception:
        return False

async def get_ip_fraud_info(ip):
    url = f"https://ipqualityscore.com/api/json/ip/{IPQS_API_KEY}/{ip}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "fraud_score": data.get("fraud_score", "N/A"),
                    "country": data.get("country_code", "N/A"),
                    "region": data.get("region", "N/A"),
                    "city": data.get("city", "N/A"),
                    "zip": data.get("zip_code", "N/A"),
                }
            else:
                return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("/getsocks5", callback_data="getsocks5"),
            InlineKeyboardButton("/check", callback_data="check"),
        ],
        [
            InlineKeyboardButton("/needip", callback_data="needip"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hello sir, how may I help you?", reply_markup=reply_markup
    )

async def getsocks5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    valid_proxies = []
    for proxy in proxy_list:
        parts = proxy.split(":")
        if len(parts) >= 2:
            ip = parts[-2]
            port = parts[-1]
            valid_proxies.append(f"{ip}:{port}")

    chunk_size = 50
    for i in range(0, len(valid_proxies), chunk_size):
        chunk = valid_proxies[i : i + chunk_size]
        message = "\n".join(chunk)
        await update.message.reply_text(message)

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please reply to this message with your proxy list (each proxy on a new line)."
    )

async def proxy_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (
        update.message.reply_to_message
        and "Please reply to this message with your proxy list" in update.message.reply_to_message.text
    ):
        text = update.message.text.strip()
        proxies = text.splitlines()

        valid_proxies = []
        for proxy in proxies:
            parts = proxy.split(":")
            if len(parts) >= 2:
                ip = parts[-2]
                port = parts[-1]
                valid_proxies.append((ip, port))

        alive_proxies = []
        await update.message.reply_text("Checking proxies, please wait...")

        for ip, port in valid_proxies[:50]:
            if await is_proxy_alive(ip, int(port)):
                alive_proxies.append(f"{ip}:{port}")

        if alive_proxies:
            await update.message.reply_text(
                "Alive proxies:\n" + "\n".join(alive_proxies)
            )
        else:
            await update.message.reply_text("No alive proxies found among those checked.")

GOKU, [07.06.2025 16:39]
async def needip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    socks5_proxies = []
    for proxy in proxy_list:
        if proxy.endswith(":1080") or "socks5" in proxy.lower():
            socks5_proxies.append(proxy)

    socks5_proxies = socks5_proxies[:10]

    if not socks5_proxies:
        await update.message.reply_text("No SOCKS5 proxies found in the list.")
        return

    await update.message.reply_text("Checking SOCKS5 proxies and fraud scores...")

    results = []
    for proxy in socks5_proxies:
        parts = proxy.split(":")
        if len(parts) < 2:
            continue
        ip = parts[-2]
        port = parts[-1]

        info = await get_ip_fraud_info(ip)
        if info:
            fraud_score = info.get("fraud_score", "N/A")
            country = info.get("country", "N/A")
            region = info.get("region", "N/A")
            city = info.get("city", "N/A")
            zip_code = info.get("zip", "N/A")
            results.append(
                f"{proxy} | Fraud Score: {fraud_score} | Location: {city}, {region}, {zip_code}, {country}"
            )
        else:
            results.append(f"{proxy} | Fraud info not available")

    await update.message.reply_text("\n".join(results))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    cmd = query.data

    if cmd == "getsocks5":
        await getsocks5(update, context)
    elif cmd == "check":
        await check_command(update, context)
    elif cmd == "needip":
        await needip(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getsocks5", getsocks5))
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(CommandHandler("needip", needip))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, proxy_list_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running...")
    app.run_polling()

if name == "main":
    main()
