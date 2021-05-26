import os
from flask import Flask, request, abort, send_file
from pytz import utc, timezone
from datetime import datetime
import threading
import queue
import time
import configparser  # 匯入config套件
import hashlib
import psycopg2
import requests
import subprocess

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
cst_tz = timezone('Asia/Taipei')  # +8時區
utc_tz = timezone('UTC')
config = configparser.ConfigParser()
config.read("./config.ini")
LineBotApiKey = (config['LineToken']['LineBotApiKey'])
WebhookHandlerKey = (config['LineToken']['WebhookHandler'])

# Channel Access Token
line_bot_api = LineBotApi(LineBotApiKey)
# Channel Secret
handler = WebhookHandler(WebhookHandlerKey)

@app.route('/')
def index():
    return "<p>Line Bot Connection To Ngrok Success!</p>"

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    UserMessage = event.message.text    
    p = subprocess.Popen('ls',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.read()
    # textMessage = p.communicate()
    print(p)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text= str(p)))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 1234))
    app.run(host='0.0.0.0', port=port)
    # ssl_context=('cert.pem', 'key.pem')