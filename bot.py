from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8990515937:AAHa04E6Vd-7BGS9PfxLreFE2cqkz0VTKKE"

# ভিডিওগুলো জমা রাখার জন্য একটি ডিকশনারি (মেমোরি ডাটাবেজ)
# ফরম্যাট: {"ভিডিওর নাম (ছোটহাতে)": "চ্যানেলের মেসেজ আইডি বা ফাইল"}
VIDEO_DATABASE = {}

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """চ্যানেলে নতুন কোনো পোস্ট বা ভিডিও আসলে বট সেটা অটোমেটিক সেভ করে নেবে"""
    message = update.channel_post
    if message and (message.video or message.document or message.text):
        caption = message.caption or message.text
        if caption:
            # ক্যাপশনের প্রথম লাইনটিকে ভিডিওর নাম হিসেবে সেভ করবে
            video_name = caption.split("\n")[0].lower().strip()
            # চ্যানেল থেকে সরাসরি মেসেজটি ইউজারের কাছে ফরোয়ার্ড করার জন্য চ্যাট আইডি ও মেসেজ আইডি সেভ রাখা
            VIDEO_DATABASE[video_name] = {
                "chat_id": message.chat_id,
                "message_id": message.message_id
            }
            print(f"নতুন ভিডিও সেভ হয়েছে: {video_name}")

async def handle_user_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইউজার বটে এসে ভিডিওর নাম লিখে সার্চ করলে বট চ্যানেল থেকে খুঁজে এনে দেবে"""
    query = update.message.text.lower().strip()
    user_name = update.message.from_user.first_name
    
    # ইউজার যদি /start লেখে
    if query == "/start":
        await update.message.reply_text(
            f"স্বাগতম {user_name}!\n\n🎬 আপনার যে ভিডিওটি প্রয়োজন, সেটির নাম লিখে এই বটে সার্চ করুন। আমি চ্যানেল থেকে খুঁজে দেব।"
        )
        return

    # ডাটাবেজে ভিডিও খোঁজা
    found = False
    for title, data in VIDEO_DATABASE.items():
        if query in title:
            found = True
            # চ্যানেল থেকে সরাসরি ভিডিওটি ইউজারের কাছে ফরোয়ার্ড করা
            await context.bot.forward_message(
                chat_id=update.effective_chat.id,
                from_chat_id=data["chat_id"],
                message_id=data["message_id"]
            )
            break
            
    if not found:
        await update.message.reply_text("❌ এই নামের কোনো ভিডিও পাওয়া যায়নি। সঠিক নাম দিয়ে আবার চেষ্টা করুন।")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # চ্যানেলের পোস্ট ট্র্যাক করার হ্যান্ডলার (বটকে চ্যানেলের অ্যাডমিন হতে হবে)
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))
    
    # ইউজারের সার্চ মেসেজ হ্যান্ডলার
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_user_search))
    application.add_handler(MessageHandler(filters.COMMAND & filters.ChatType.PRIVATE, handle_user_search))
    
    print("অটো-ইনডেক্সিং বট সফলভাবে চালু হয়েছে...")
    application.run_polling()

if __name__ == '__main__':
    main()
