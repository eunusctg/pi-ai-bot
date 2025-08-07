<details>
<summary>Click to show code</summary>

import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

user_modes = {}
models = {
    "chatbot": "meta-llama/Llama-2-7b-chat-hf",
    "summarize": "facebook/bart-large-cnn",
    "imagegen": "stabilityai/stable-diffusion-2"
}
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 Welcome to PI AI Bot!\n\nUse commands:\n/chatbot\n/summarize\n/imagegen"
    )

def set_mode(update: Update, context: CallbackContext, mode: str):
    user_id = update.effective_user.id
    user_modes[user_id] = mode
    update.message.reply_text(f"✅ Mode set to {mode.upper()}.\nSend your input:")

def chatbot(update: Update, context: CallbackContext):
    set_mode(update, context, "chatbot")

def summarize(update: Update, context: CallbackContext):
    set_mode(update, context, "summarize")

def imagegen(update: Update, context: CallbackContext):
    set_mode(update, context, "imagegen")

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    mode = user_modes.get(user_id)
    if not mode:
        update.message.reply_text("Choose a mode:\n/chatbot /summarize /imagegen")
        return

    user_input = update.message.text
    model_id = models[mode]
    payload = {"inputs": user_input}

    if mode == "imagegen":
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            update.message.reply_photo(photo=response.content)
        else:
            update.message.reply_text("Image generation failed.")
    else:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers=headers,
            json=payload
        )
        result = response.json()
        if isinstance(result, list) and 'summary_text' in result[0]:
            reply = result[0]['summary_text']
        elif isinstance(result, dict) and 'generated_text' in result:
            reply = result['generated_text']
        else:
            reply = "❌ Could not get response from model."
        update.message.reply_text(reply)

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("chatbot", chatbot))
    dp.add_handler(CommandHandler("summarize", summarize))
    dp.add_handler(CommandHandler("imagegen", imagegen))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

</details>
