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
#     return send_file(file_to_be_sent, as_atta


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
    UserMessageAddSplitCheck = False
    UserMessageSearchSplitCheck = False
    try:
        UserMessageAddSplit = str(UserMessage).split("|")
        if(len(UserMessageAddSplit) >= 2):
            UserMessageAddSplitCheck = True
    except Exception as AddSplitError:
        pass

    try:
        UserMessageSearchSplit = str(UserMessage).split("-")
        if(len(UserMessageSearchSplit) >= 2):
            UserMessageSearchSplitCheck = True
    except Exception as SearchSplitError:
        pass

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
#    line_bot_api.reply_message(event.reply_token, flex_message)

    if (str(UserMessage)[0].upper() == "P" and str(UserMessage)[1:len(str(UserMessage))].isdigit() == True):
        ReturnMessage = SearchPersonalNumberInDatabase(UserMessage.upper())
        if (str(ReturnMessage) == "[]" or str(ReturnMessage) == "list index out of range"):
            NullErrorMessage = "尚未在資料庫收尋到相關資料！"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text= NullErrorMessage))
        else:
            line_bot_api.reply_message(event.reply_token, ReturnMessage)
    elif (UserMessageAddSplitCheck == True):
        if (UserMessageAddSplit[0] == "新增會員"):
            ReturnMessage = InsertToDatabase(UserMessageAddSplit)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ReturnMessage))
    elif (UserMessageSearchSplitCheck == True):
        if (UserMessageSearchSplit[0] == "收尋"):
            ReturnMessage = SearchPersonalNameInDatabase(UserMessageSearchSplit)
            if (str(ReturnMessage) == "[]" or str(ReturnMessage) == "list index out of range" or str(ReturnMessage).split(" ")[0] == "unterminated"):
                NullErrorMessage = "尚未在資料庫收尋到相關資料！"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text= NullErrorMessage))
            else:
                print(ReturnMessage)
                print(type(ReturnMessage))
                line_bot_api.reply_message(event.reply_token, ReturnMessage)
    elif (UserMessage == "Delete" or UserMessage == "刪除"):
        ReturnMessage = DeleteToDatabase()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ReturnMessage))
    elif (UserMessage == "收尋" or UserMessage == "Search"):
        ReturnMessage = SearchInDatabase()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ReturnMessage))
    elif (UserMessage == "把加幹進去"):
        ReturnMessage = SearchUserIdInDatabase(event)
        if (ReturnMessage == True):
            ReturnMessage = "你擁有資格可以加進資料庫！"
            # ReturnMessage = InsertUserTable(event)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ReturnMessage))
        else:
            ReturnMessage = "您的權限不足，詳情請洽管理人員！！"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ReturnMessage))
    else:
        ReturnMessage = "請依照格式輸入！！"
        UserName = GetPersonaName(str(event.source.user_id))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text= str(UserName) + "你的ID為：" + str(event.source.user_id)))
        # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=UserName + "你媽死了"))

def InsertToDatabase(InsertArray):
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(
            config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        cur.execute("INSERT INTO membertable(membername, membernumber, memberavatar, membertickettype) VALUES ('" + InsertArray[1] + "', '" + InsertArray[2] + "', '" + InsertArray[3] + "', '" + InsertArray[4] + "')")
        conn.commit()
        cur.close()
        InsertSuccessMessage = "會員編號：" + str(InsertArray[1]) + "，新增成功！！"
        return InsertSuccessMessage
    except Exception as InsertErrorMessage:
        return str(InsertErrorMessage)

def DeleteToDatabase():
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        cur.execute("DELETE from membertable")
        conn.commit()
        cur.close()
        DeleteSuccessMessage = "全數刪除成功！！"
        return DeleteSuccessMessage
    except Exception as DeleteErrorMessage:
        return str(DeleteErrorMessage)

def SearchInDatabase():
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        cur.execute("SELECT * FROM membertable")
        rows = cur.fetchall()
        SerachData = ""
        for row in rows:
            SerachData = SerachData + str(row) + "\n\n"
        conn.commit()
        cur.close()
        DataInsertToFlexSendMessage
        SearchSuccessMessage = SerachData
        return SearchSuccessMessage
    except Exception as SearchErrorMessage:
        return str(SearchErrorMessage)

def SearchPersonalNameInDatabase(SearchArray):
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        cur.execute("SELECT * FROM membertable WHERE membername = '" + SearchArray[1] + "'")
        SerachPersonalNameData = cur.fetchall()
        conn.commit()
        cur.close()
        SearchPersonalNameSuccessMessage = DataInsertToFlexSendMessage(SerachPersonalNameData)
        return SearchPersonalNameSuccessMessage
    except Exception as SearchErrorMessage:
        return str(SearchErrorMessage)

def SearchPersonalNumberInDatabase(membernumber):
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        cur.execute("SELECT * FROM membertable WHERE membernumber = '" + membernumber + "'")
        SerachPersonalNumberData = cur.fetchall()
        conn.commit()
        cur.close()
        SearchPersonalNumberSuccessMessage = DataInsertToFlexSendMessage(SerachPersonalNumberData)
        return SearchPersonalNumberSuccessMessage
    except Exception as SearchErrorMessage:
        return str(SearchErrorMessage)

def SearchUserIdInDatabase(event):
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        cur.execute("SELECT * FROM usertable WHERE userid = '" + event.source.user_id + "'")
        SearchUserIdCheck = True
        conn.commit()
        cur.close()
        return SearchUserIdCheck
    except Exception as SearchErrorMessage:
        SearchUserIdCheck = False
        return SearchUserIdCheck

def DataInsertToFlexSendMessage(DataList):
    
    if (str(DataList[0][3]) == "一般票"):
        colorCode = "#D94600"
    elif (str(DataList[0][3]) == "優待票"):
        colorCode = "#FFD306"
    elif (str(DataList[0][3]) == "限時票"):
        colorCode = "#0000C6"
        
    flex_message = FlexSendMessage(
        alt_text='hello',
        contents={
            "type": "bubble", 
            "hero": {
                "type": "image", 
                "url": DataList[0][2], 
                "size": "full", 
                "aspectRatio": "20:13", 
                "aspectMode": "cover", 
                "action": {
                    "type": "uri", 
                    "uri": "https://www.google.com/"
                }
            }, 
            "body": {
                "type": "box", 
                "layout": "vertical", 
                "contents": [
                    {
                        "type": "text", 
                        "weight": "bold", 
                        "size": "xl", 
                        "contents": [
                            {
                                "type": "span", 
                                "text": "會籍編號："
                            }, 
                            {
                                "type": "span", 
                                "text": DataList[0][1]
                            }
                        ]
                    }, 
                    {
                        "type": "box", 
                        "layout": "baseline", 
                        "margin": "md", 
                        "contents": [
                            {
                                "type": "text", 
                                "text": "會員票種：優待票、限時票、一般票", 
                                "contents": [
                                    {
                                        "type": "span", 
                                        "text": "會員票種："
                                    }, 
                                    {
                                        "type": "span", 
                                        "text": DataList[0][3],
                                        "weight": "bold", 
                                        "style": "normal", 
                                        "size": "lg", 
                                        "color": colorCode
                                    }
                                ]
                            }
                        ]
                    }, 
                    {
                        "type": "box", 
                        "layout": "baseline", 
                        "margin": "md", 
                        "contents": [
                            {
                                "type": "text", 
                                "text": "會員名稱", 
                                "contents": [
                                    {
                                        "type": "span", 
                                        "text": "會員名稱："
                                    }, 
                                    {
                                        "type": "span", 
                                        "text": DataList[0][0]
                                    }
                                ]
                            }
                        ]
                    }, 
                    {
                        "type": "box", 
                        "layout": "vertical", 
                        "margin": "lg", 
                        "spacing": "sm", 
                        "contents": [
                            {
                                "type": "box", 
                                "layout": "baseline", 
                                "contents": [
                                    {
                                        "type": "text", 
                                        "text": "起始日：", 
                                        "size": "sm", 
                                        "color": "#aaaaaa"
                                    }, 
                                    {
                                        "type": "text", 
                                        "text": "2021-05-01", 
                                        "flex": 3, 
                                        "size": "sm", 
                                        "color": "#666666"
                                    }
                                ]
                            }, 
                            {
                                "type": "box", 
                                "layout": "baseline", 
                                "contents": [
                                    {
                                        "type": "text", 
                                        "text": "到期日：", 
                                        "size": "sm", 
                                        "color": "#aaaaaa"
                                    }, 
                                    {
                                        "type": "text", 
                                        "text": "2022-05-01", 
                                        "flex": 3, 
                                        "size": "sm", 
                                        "color": "#666666"
                                    }
                                ]
                            }, 
                            {
                                "type": "separator"
                            },
                            {
                                "type": "box", 
                                "layout": "baseline", 
                                "spacing": "sm", 
                                "contents": [
                                    {
                                        "type": "text", 
                                        "text": "進場：", 
                                        "color": "#aaaaaa", 
                                        "size": "sm", 
                                        "flex": 1
                                    }, 
                                    {
                                        "type": "text", 
                                        "text": "2021-05-02 14:01:20", 
                                        "wrap": True, 
                                        "color": "#666666", 
                                        "size": "sm", 
                                        "flex": 5
                                    }
                                ]
                            }, 
                            {
                                "type": "box", 
                                "layout": "baseline", 
                                "spacing": "sm", 
                                "contents": [
                                    {
                                        "type": "text", 
                                        "text": "離場：", 
                                        "color": "#aaaaaa", 
                                        "size": "sm", 
                                        "flex": 1
                                    }, 
                                    {
                                        "type": "text", 
                                        "text": "2021-05-02 15:30:14", 
                                        "wrap": True, 
                                        "color": "#666666", 
                                        "size": "sm", 
                                        "flex": 5
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }, 
            "footer": {
                "type": "box", 
                "layout": "vertical", 
                "spacing": "sm", 
                "contents": [
                    {
                        "type": "button", 
                        "style": "link", 
                        "height": "sm", 
                        "action": {
                            "type": "uri", 
                            "label": "進場", 
                            "uri": "https://www.google.com/"
                        }
                    }, 
                    {
                        "type": "button", 
                        "style": "link", 
                        "height": "sm", 
                        "action": {
                            "type": "uri", 
                            "label": "離場", 
                            "uri": "https://www.google.com/"
                        }
                    }
                ], 
                "flex": 0
            }
        }
    )
    return flex_message

def GetPersonaName(userid):
    URL = "https://api.line.me/v2/bot/profile/" + userid
    header = {'Authorization': 'Bearer ' + LineBotApiKey + "'"}
    ReturnRequests = requests.get(URL, headers = header)
    return str(ReturnRequests.json()['displayName'])

def InsertUserTable(event):
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(
            config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        UserName = GetPersonaName(str(event.source.user_id))
        cur.execute("INSERT INTO usertable(username, userid) VALUES ('" + str(UserName) + "', '" + str(event.source.user_id) + "')")
        conn.commit()
        cur.close()
        InsertSuccessMessage = "已經把" + str(UserName) + "加入UserTable中！，UserId：" + str(event.source.user_id) + "，新增成功！！"
        return InsertSuccessMessage
    except Exception as InsertErrorMessage:
        return str(InsertErrorMessage)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 300))
    app.run(host='0.0.0.0', port=port)
    # ssl_context=('cert.pem', 'key.pem')