import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
from ip_check import check_ip
from utils import fetch_socks5_proxies, filter_by_location

API_KEY = "ZLsvHEr0d0MWIo3E4vDivecwUjeLKl0s"

async def getproxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Checking live proxies (dummy response).")

async def scrapeproxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proxies = await fetch_socks5_proxies()
    await update.message.reply_text("\n".join(proxies[:50]))

async def getsocks5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Scraping SOCKS5 proxies and checking fraud scores...")
    proxies = await fetch_socks5_proxies()
    reply = []

    for proxy in proxies[:20]:
        ip, port = proxy.split(":")
        data = check_ip(ip, API_KEY)

        if data and data.get("success"):
            fraud_score = data.get("fraud_score", "N/A")
            country = data.get("country_code", "N/A")
            region = data.get("region", "N/A")
            zip_code = data.get("zip_code", "N/A")
            reply.append(f"🧩 `{ip}:{port}`\n🌍 {country}, {region}, {zip_code}\n⚠️ Fraud Score: *{fraud_score}*\n")
        await asyncio.sleep(1)

    if not reply:
        await update.message.reply_text("❌ No valid SOCKS5 proxies found.")
    else:
        await update.message.reply_text("\n\n".join(reply), parse_mode="Markdown")

async def needip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❗ Please provide a ZIP, state, or country.")
        return
    proxies = await fetch_socks5_proxies()
    result = []
    for proxy in proxies[:30]:
        ip, port = proxy.split(":")
        data = check_ip(ip, API_KEY)
        if data and data.get("success"):
            if query.lower() in str(data.get("zip_code", "")).lower() or                query.lower() in str(data.get("region", "")).lower() or                query.lower() in str(data.get("country_code", "")).lower():
                fraud_score = data.get("fraud_score", "N/A")
                country = data.get("country_code", "N/A")
                region = data.get("region", "N/A")
                zip_code = data.get("zip_code", "N/A")
                result.append(f"🧩 `{ip}:{port}`\n🌍 {country}, {region}, {zip_code}\n⚠️ Fraud Score: *{fraud_score}*\n")
        await asyncio.sleep(1)
    if not result:
        await update.message.reply_text("❌ No matching proxies found.")
    else:
        await update.message.reply_text("\n\n".join(result), parse_mode="Markdown")

if __name__ == "__main__":
    BOT_TOKEN = "7616386838:AAGAJeWB0Z4OG1PMshVIrcEpwXD8yaOj0S0"
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("getproxy", getproxy))
    app.add_handler(CommandHandler("scrapeproxy", scrapeproxy))
    app.add_handler(CommandHandler("getsocks5", getsocks5))
    app.add_handler(CommandHandler("needip", needip))
    print("🤖 Bot running...")
    app.run_polling()
