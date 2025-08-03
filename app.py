from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Channel access token 和 secret（從環境變數讀取）
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

# 發言紀錄（user_id -> [timestamps]）
message_counts = defaultdict(list)

# 管理員列表（請填入實際的 LINE user ID）
ADMINS = {"YOUR_ADMIN_USER_ID"}

@app.route("/")
def home():
    return "LINE Bot is running."

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    now = datetime.now()

    # 檢查是否為管理員
    if user_id not in ADMINS:
        today_messages = [
            ts for ts in message_counts[user_id]
            if ts.date() == now.date()
        ]
        if len(today_messages) >= 10:
            line_bot_api.delete_message(event.message.id)
            return
        message_counts[user_id].append(now)

    # 回應用戶訊息（測試用）
    line_bot_api.reply_message(
        event.reply_token,
        event.message
    )

if __name__ == "__main__":
    app.run()
