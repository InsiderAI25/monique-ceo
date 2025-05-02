
from flask import Flask, request
import telegram
import os

app = Flask(__name__)
bot_token = os.environ.get("BOT_TOKEN")
bot = telegram.Bot(token=bot_token)

@app.route('/')
def home():
    return 'Monique AI (CEO) is live.'

@app.route(f'/{bot_token}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.effective_chat.id
    text = update.message.text if update.message else ''

    if text.startswith('/status'):
        bot.send_message(chat_id=chat_id, text="👩‍💼 Monique is active and overseeing operations.")
    elif text.startswith('/override'):
        bot.send_message(chat_id=chat_id, text="🛡️ Override command received. Awaiting execution authority.")
    elif text.startswith('/approve'):
        bot.send_message(chat_id=chat_id, text="✅ Approval logged and synced with Vaultkeeper.")
    elif text.startswith('/reassign'):
        bot.send_message(chat_id=chat_id, text="🔁 Logic reassignment request acknowledged.")
    elif text.startswith('/check_logic'):
        bot.send_message(chat_id=chat_id, text="🧠 Initiating logic review...")
    else:
        bot.send_message(chat_id=chat_id, text="📘 Command received by Monique AI.")

    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
