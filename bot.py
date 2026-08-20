import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = "8899456179:AAE1TFmllNqqtAYs3rgOylJDRWK7GcsH5no"
ADMIN_ID = 8123711856
BKASH_NUMBER = "01617184801"
NAGAD_NUMBER = "01898916288"

WAITING_PAYMENT_PROOF = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("1. ON 🟢", callback_data="btn_on")],
        [InlineKeyboardButton("2. OFF 🔴", callback_data="btn_off")],
        [InlineKeyboardButton("3. BOT SENT ANOTHER GUILD 🌐", callback_data="btn_guild")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("নিচের অপশনগুলো থেকে বেছে নিন:", reply_markup=reply_markup)
    return ConversationHandler.END

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "btn_off":
        user = query.from_user
        await query.edit_message_text(text="Your request is pending for Admin approval... ⏳")

        admin_keyboard = [
            [InlineKeyboardButton("Approve Success ✅", callback_data=f"approve_{query.message.chat_id}_{query.message.message_id}")]
        ]
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚨 **OFF Request Received**\nUser: {user.full_name} (@{user.username})\nID: `{user.id}`",
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif query.data in ["btn_on", "btn_guild"]:
        amount = "2 TK" if query.data == "btn_on" else "50 TK"
        service = "BOT ON" if query.data == "btn_on" else "BOT SENT ANOTHER GUILD"
        context.user_data['service_type'] = service

        text_msg = (
            f"💳 **Payment Details**\n\n"
            f"📱 **bKash:** `{BKASH_NUMBER}`\n"
            f"📱 **Nagad:** `{NAGAD_NUMBER}`\n\n"
            f"**SEND MONEY ({amount})**\n\n"
            "পেমেন্ট করার পরে আপনার Transaction ID (TrxID) + SCREEN SHOT পাঠাতে নিচের বাটনে চাপ দিন।"
        )
        keyboard = [[InlineKeyboardButton("SEND PROOF 💸", callback_data="btn_paid")]]
        await query.edit_message_text(text=text_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return ConversationHandler.END

    elif query.data == "btn_paid":
        await query.edit_message_text(
            text="ধন্যবাদ! এবার আপনার **Transaction ID (TrxID)** এবং **SCREEN SHOT** মেসেজে একসাথে পাঠান।"
        )
        return WAITING_PAYMENT_PROOF

    elif query.data.startswith("approve_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("আপনি এডমিন নন!", show_alert=True)
            return ConversationHandler.END

        _, user_chat_id, user_msg_id = query.data.split("_")
        try:
            await context.bot.edit_message_text(
                chat_id=int(user_chat_id),
                message_id=int(user_msg_id),
                text="SUCCESS ✅"
            )
            await query.edit_message_text(text="Approved successfully! ✅")
        except Exception as e:
            await query.edit_message_text(text=f"Error: {str(e)}")
        return ConversationHandler.END

async def receive_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    service = context.user_data.get('service_type', 'Payment Request')

    sent_msg = await update.message.reply_text("আপনার পেমেন্ট তথ্য জমা হয়েছে, এডমিন ভেরিফাই করছেন... ⏳")

    admin_keyboard = [
        [InlineKeyboardButton("Approve Success ✅", callback_data=f"approve_{update.message.chat_id}_{sent_msg.message_id}")]
    ]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 **New Payment Request Received**\n\n"
             f"👤 User: {user.full_name} (@{user.username})\n"
             f"🆔 User ID: `{user.id}`\n"
             f"🛠 Service: {service}",
        parse_mode="Markdown"
    )
    
    await context.bot.copy_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        reply_markup=InlineKeyboardMarkup(admin_keyboard)
    )

    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_click, pattern="^btn_paid$")
        ],
        states={
            WAITING_PAYMENT_PROOF: [
                MessageHandler(filters.TEXT | filters.PHOTO, receive_payment_proof)
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
      
