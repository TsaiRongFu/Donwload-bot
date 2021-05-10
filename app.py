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
    return "<p>Line Bot Connection To Herouk Success!</p>"

# @app.route('/.well-known/pki-validation/C1AF4ADAC03A064EADE53CD54C66E8F0.txt', methods=["GET"])
# def send():
#     file_to_be_sent = "C1AF4ADAC03A064EADE53CD54C66E8F0.txt"
#     return send_file(file_to_be_sent, as_attachment=True)


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
    UserMessageSplitCheck = False
    try:
        UserMessageSplit = UserMessage.split(str="-")
        UserMessageSplitCheck = True
    except:
        pass
#    time.sleep(30)
    reply_text1 = "1234"
    reply_text = "123"

    sticker_message = StickerSendMessage(
        package_id='6325', sticker_id='10979905')
#    emoji = {"index": 0, "productId": "5ac2173d031a6752fb806d56", "emojiId": "093"}
#    emoji1 = {"index": 5, "productId": "5ac1de17040ab15980c9b438", "emojiId": "001"}
#    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), sticker_message ,TextSendMessage(text="$Eggs$", emojis=[emoji,emoji1])])
#    多個
    emoji = [{"index": 0, "productId": "5ac1bfd5040ab15980c9b435", "emojiId": "001"}]
#    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), sticker_message ,TextSendMessage(text="$Eggs", emojis=emoji)])
#    多訊息Line最多上限5則
#    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])
#    TextSendMessage(text= replyMsg)
#    GoogleWeb = "https://www.google.com/"
#    flex_message = FlexSendMessage(
#        alt_text='hello',
#        contents={
#            "type": "bubble",
#            "hero": {
#                "type": "image",
#                "url": "https://lh3.googleusercontent.com/fife/ABSRlIokHUI0NDnw524TNzlQqWC5jBZzfi_ssEAC5tmZWTGb08HbsHUFM_zrH05tNdQqbxEPHtxoLwsmuNxroTd1j0CjbKWz6OQUxsXJ3ZHBVnjTgCtB6TR2FcE6itppuSQCKJQLpWzQdAKC77zL4LY18zg9sS-Abp0qdMZ2hZ0Y6TpUNJH_VfxnOVA5MBSjgY7q78LxJ2bq9q2N67HOR6C3uXO0mubc5WjjyRTxpurcE2X-H59p2cJVYCR9DnG4hoe6byMyM8IYUst6v2vestukNwYJN6iwrLCFuVomCdxbzWm50DSY1lVMB-H1v_4Udp_6Hj5kIovtFrxdb8qgTe1wb8E_LrbhEOFqWe6izlceVja9nrWYU4Cg86TlCc4R3VdLdqUufwQeBPvaq5GIHWZ4wSrtJ1a_MYvlsi6SgOR3lB4f8a142sQO5fbpTSIHjj8Hl-tTeFwYjpVAtjkiXI8bpX1ouxFZ5dyuqmGZBUjAc3EOja2m3Q2Z10PXW3NdyLUHDEPxsHeLQIbIVE6Gr0Gq_ACBZuQAL2ju2V9w5hnn0kHKFxfC-EynUn3zupc3UwEhF_Yeqn8bPTl5gmRUuxigznwRgfXv5gtCLhKQNOBZaS1fJ5odrpCAPuf4wDJDsR80dMs1ffkQS-70Q59SPK1yRfSHvZP_ats0ZPdeUY0losJDX9kEphc_3EwD76eSp9C6_jlbsHE3xqgBJ_SmpdtB1dw4VxZtAIkbJhc=w1920-h969-ft",
#                "size": "full",
#                "aspectRatio": "20:13",
#                "aspectMode": "cover",
#                "action": {
#                    "type": "uri",
#                    "uri": GoogleWeb
#                }
#            },
#            "body": {
#                "type": "box",
#                "layout": "vertical",
#                "contents": [
#                    {
#                        "type": "text",
#                        "text": "會籍編號：P077",
#                        "weight": "bold",
#                        "size": "xl"
#                    },
#                    {
#                        "type": "box",
#                        "layout": "baseline",
#                        "margin": "md",
#                        "contents": [
#                            {
#                                "type": "text",
#                                "text": "會員票種：優待票、限時票、一般票",
#                                "contents": [
#                                    {
#                                        "type": "span",
#                                        "text": "會員票種："
#                                    },
#                                    {
#                                        "type": "span",
#                                        "text": "優待票、限時票、一般票",
#                                        "weight": "bold",
#                                        "style": "normal",
#                                        "size": "lg",
#                                        "color": "#FFA500"
#                                    }
#                                ]
#                            }
#                        ]
#                    },
#                    {
#                        "type": "box",
#                        "layout": "vertical",
#                        "margin": "lg",
#                        "spacing": "sm",
#                        "contents": [
#                            {
#                                "type": "box",
#                                "layout": "baseline",
#                                "spacing": "sm",
#                                "contents": [
#                                    {
#                                        "type": "text",
#                                        "text": "進場：",
#                                        "color": "#aaaaaa",
#                                        "size": "sm",
#                                        "flex": 1
#                                    },
#                                    {
#                                        "type": "text",
#                                        "text": "2021-05-02 14:01:20",
#                                        "wrap": True,
#                                        "color": "#666666",
#                                        "size": "sm",
#                                        "flex": 5
#                                    }
#                                ]
#                            },
#                            {
#                                "type": "box",
#                                "layout": "baseline",
#                                "spacing": "sm",
#                                "contents": [
#                                    {
#                                        "type": "text",
#                                        "text": "離場：",
#                                        "color": "#aaaaaa",
#                                        "size": "sm",
#                                        "flex": 1
#                                    },
#                                    {
#                                        "type": "text",
#                                        "text": "2021-05-02 15:30:14",
#                                        "wrap": True,
#                                        "color": "#666666",
#                                        "size": "sm",
#                                        "flex": 5
#                                    }
#                                ]
#                            }
#                        ]
#                    }
#                ]
#            },
#            "footer": {
#                "type": "box",
#                "layout": "vertical",
#                "spacing": "sm",
#                "contents": [
#                    {
#                        "type": "button",
#                        "style": "link",
#                        "height": "sm",
#                        "action": {
#                            "type": "uri",
#                            "label": "進場",
#                            "uri": "https://www.google.com/"
#                        }
#                    },
#                    {
#                        "type": "button",
#                        "style": "link",
#                        "height": "sm",
#                        "action": {
#                            "type": "uri",
#                            "label": "離場",
#                            "uri": "https://www.google.com/"
#                        }
#                    },
#                ],
#                "flex": 0
#            }
#        }
#    )
#    line_bot_api.reply_message(event.reply_token, flex_message)
    if (UserMessageSplitCheck = True):
        if (UserMessageSplit[0] == "新增會員"):
            ReturnMessage = InsertToDatabase(event,UserMessage)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = ReturnMessage))
    else:
        ReturnMessage = "請依照格式輸入！！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = ReturnMessage))
    

def InsertToDatabase(event,InsertArray):
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        cur.execute("INSERT INTO membertable(membername, membernumber, memberavatar, membertickettype) VALUES('" + InsertArray[0] +"', '" + InsertArray[1] + "', '" + InsertArray[2] + "', '" + InsertArray[3] + "')")
        conn.commit()
        cur.close()
        InsertSuccessMessage = "會員編號：" + str(InsertArray[1]) + "，新增成功！！"
        return InsertSuccessMessage
    except Exception as InsertErrorMessage:
        return str(InsertErrorMessage)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 300))
    app.run(host='0.0.0.0', port=port)
    #ssl_context=('cert.pem', 'key.pem')

