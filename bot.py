import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- Dummy Web Server to fix Render Port Timeout ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- Logging setup ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ⚠️ Admin ID & Correct Bot Token
ADMIN_ID = 8123711856 
BOT_TOKEN = "8899456179:AAE1TFmllNqqtAYs3rgOylJDRWK7GcsH5no"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1. ON 🟢", callback_data="btn_on")],
        [InlineKeyboardButton("2. OFF 🔴", callback_data="btn_off")],
        [InlineKeyboardButton("3. BOT SENT ANOTHER GUILD 🤖", callback_data="btn_guild")],
        [InlineKeyboardButton("4. CREATE NEW BOT 🚀", callback_data="btn_create_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("নিচের অপশনগুলো থেকে একটি বেছে নিন:", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if query.data == "btn_on":
        await query.edit_message_text("⏳ **Processing...** Please wait.", parse_mode="Markdown")
        
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Approve ✅", callback_data=f"approve_{query.message.chat_id}_{query.message.message_id}"),
                InlineKeyboardButton("Reject ❌", callback_data=f"reject_{query.message.chat_id}_{query.message.message_id}")
            ]
        ])
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚨 **ON Request**\nUser: {user.full_name}\nID: `{user.id}`",
            reply_markup=admin_keyboard,
            parse_mode="Markdown"
        )

    elif query.data == "btn_off":
        await query.edit_message_text("⏳ **Processing...** Please wait.", parse_mode="Markdown")
        
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Approve ✅", callback_data=f"approve_{query.message.chat_id}_{query.message.message_id}"),
                InlineKeyboardButton("Reject ❌", callback_data=f"reject_{query.message.chat_id}_{query.message.message_id}")
            ]
        ])
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚨 **OFF Request**\nUser: {user.full_name}\nID: `{user.id}`",
            reply_markup=admin_keyboard,
            parse_mode="Markdown"
        )

    elif query.data == "btn_guild":
        msg_text = (
            "🤖 **BOT SENT ANOTHER GUILD**\n\n"
            "ফি: **50 TK**\n\n"
            "💳 **Payment Details**\n"
            "bKash: `01617184801`\n"
            "Nagad: `01898916288`\n\n"
            "পেমেন্ট করার পরে আপনার Screen Shot & Transaction ID (TrxID) পাঠান।"
        )
        await query.edit_message_text(msg_text, parse_mode="Markdown")

    elif query.data == "btn_create_bot":
        msg_text = (
            "🚀 **CREATE NEW BOT**\n\n"
            "ফি: **150 TK**\n\n"
            "💳 **Payment Details**\n"
            "bKash: `01617184801`\n"
            "Nagad: `01898916288`\n\n"
            "পেমেন্ট করার পরে আপনার Screen Shot & Transaction ID (TrxID) পাঠান।"
        )
        await query.edit_message_text(msg_text, parse_mode="Markdown")

    elif query.data.startswith("approve_"):
        data_parts = query.data.split("_")
        user_chat_id = int(data_parts[1])
        user_msg_id = int(data_parts[2])

        await query.edit_message_text("✅ **Approved Successfully!**", parse_mode="Markdown")

        try:
            await context.bot.edit_message_text(
                chat_id=user_chat_id,
                message_id=user_msg_id,
                text="✅ **Successful!** Your request has been completed.",
                parse_mode="Markdown"
            )
        except Exception:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="✅ **Successful!** Your request has been completed."
            )

    elif query.data.startswith("reject_"):
        data_parts = query.data.split("_")
        user_chat_id = int(data_parts[1])
        user_msg_id = int(data_parts[2])

        await query.edit_message_text("❌ **Request Rejected!**", parse_mode="Markdown")

        try:
            await context.bot.edit_message_text(
                chat_id=user_chat_id,
                message_id=user_msg_id,
                text="❌ **Rejected!** Invalid Payment / Transaction ID or Request.",
                parse_mode="Markdown"
            )
        except Exception:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="❌ **Rejected!** Invalid Payment / Transaction ID or Request."
            )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    caption = f"📩 **Payment Proof Received!**\nUser: {user.full_name}\nID: `{user.id}`"

    processing_msg = await update.message.reply_text("⏳ **Processing...** Checking your payment.", parse_mode="Markdown")

    admin_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Approve ✅", callback_data=f"approve_{update.message.chat_id}_{processing_msg.message_id}"),
            InlineKeyboardButton("Reject ❌", callback_data=f"reject_{update.message.chat_id}_{processing_msg.message_id}")
        ]
    ])

    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
        user_text = update.message.caption if update.message.caption else "No Text"
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=f"{caption}\n**TrxID:** {user_text}",
            reply_markup=admin_keyboard,
            parse_mode="Markdown"
        )
    elif update.message.text:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"{caption}\n**TrxID:** {update.message.text}",
            reply_markup=admin_keyboard,
            parse_mode="Markdown"
        )

if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    app.run_polling()
    
