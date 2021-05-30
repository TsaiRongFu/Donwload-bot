from __future__ import unicode_literals
import os
from flask import Flask, request, abort, send_file
from pytz import utc, timezone
from datetime import datetime
import configparser  # 匯入config套件
import requests
import youtube_dl
import psycopg2
import threading
import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

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
settings_path = 'settings.yaml'
# gauth = GoogleAuth(settings_file=settings_path)
# # gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    UserMessage = event.message.text    
    CheckWhereRegister = SerachRegisterInDatabase(event)

    if (CheckWhereRegister == False):
        if (UserMessage.lower() == "register" or UserMessage.lower() == "註冊"):
            Messages = RegisterToDatabase(event)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Messages))
        elif (UserMessage == "使用說明"):
            Messages = "如果要下載影片請輸入:mp4-影片網址\n\n如果要音樂影片請輸入:mp3-音樂網址"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Messages))
        else:    
            Messages = str(GetPersonaName(event.source.user_id))+ "" + "你好！\n\n目前此功能只提供給註冊用戶使用，目前開放註冊到5/31。\n\n如您需要註冊請輸入：Register"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Messages))
    elif (CheckWhereRegister == True):
        if (UserMessage.lower() == "register" or UserMessage.lower() == "註冊"):
            Messages = str(GetPersonaName(event.source.user_id)) + "，您已經註冊成功了！\n\n使用說明如下：\n\n如果要下載影片請輸入:mp4-影片網址\n\n如果要音樂影片請輸入:mp3-音樂網址"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Messages))
        elif (UserMessage == "使用說明"):
            Messages = "如果要下載影片請輸入:mp4-影片網址\n\n如果要音樂影片請輸入:mp3-音樂網址"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Messages))
        elif ((UserMessage.split("-")[0]).lower() == "mp3" or UserMessage.split("-")[0] == "音樂"):
            try:
                video_info = get_video_info(UserMessage.split("-")[1])
                ydl_opts_mp3 = {
                    'outtmpl': StringProcess(str(video_info['標題'])) + ".mp3",
                    'format': "bestaudio/best",
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'logger': MyLogger(),
                    'progress_hooks': [my_hook],
                }
                FileName = str(video_info['標題'])
                with youtube_dl.YoutubeDL(ydl_opts_mp3) as ydl:
                    ydl.download([UserMessage.split("-")[1]])
                    Messages = FileName + "，下載完畢！\n\n正在上傳，稍後可以在以下網址，您的資料夾內找到檔案！\n\nhttps://tinyurl.com/3vr8fus3"
                    FolderId = CheckFileInDrive(event,settings_path)
                    # UploadFile(FolderId, str(StringProcess(str(video_info['標題']))) + ".mp3")
                    t = threading.Thread(target = UploadFile, args = (FolderId, str(StringProcess(str(video_info['標題']))) + ".mp3"))
                    t.start()
            except Exception as InsertErrorMessage:
                Messages = str(InsertErrorMessage)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Messages))
        elif ((UserMessage.split("-")[0]).lower() == "mp4" or UserMessage.split("-")[0] == "影片"):
            try:
                video_info = get_video_info(UserMessage.split("-")[1])
                ydl_opts_mp4 = {
                    'outtmpl': StringProcess(str(video_info['標題'])) + ".mp4",
                    'format': "bestvideo[ext=mp4]+bestaudio/best",
                    'logger': MyLogger(),
                    'progress_hooks': [my_hook],
                }
                FileName = str(video_info['標題'])
                with youtube_dl.YoutubeDL(ydl_opts_mp4) as ydl:
                    ydl.download([UserMessage.split("-")[1]])
                    Messages = FileName + "，下載完畢！\n\n正在上傳，稍後可以在以下網址，您的資料夾內找到檔案！\n\nhttps://tinyurl.com/3vr8fus3"
                    FolderId = CheckFileInDrive(event,settings_path)
                    # UploadFile(FolderId, str(StringProcess(str(video_info['標題']))) + ".mp4")
                    t = threading.Thread(target = UploadFile, args = (FolderId, str(StringProcess(str(video_info['標題']))) + ".mp4"))
                    t.start()
            except Exception as InsertErrorMessage:
                Messages = str(InsertErrorMessage)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Messages))
        else:
            Messages = "請輸入正確格式！"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Messages))
    else:
        Messages = "請輸入正確格式！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Messages))   

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

def get_video_info(youtube_url):
    video_info = {}

    with youtube_dl.YoutubeDL() as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        # pprint(info)
        video_info['ID'] = info.get('id')
        video_info['標題'] = info.get('title')
        video_info['影片縮圖'] = info.get('thumbnail')
        video_info['上傳者'] = info.get('uploader')
        video_info['上傳者網址'] = info.get('uploader_url')
        video_info['影片長度(秒)'] = info.get('duration')
        video_info['觀看次數'] = info.get('view_count')
        video_info['留言數'] = info.get('comment_count') # -
        video_info['喜歡數'] = info.get('like_count')
        video_info['不喜歡數'] = info.get('dislike_count')
        video_info['平均評分'] = info.get('average_rating')
        video_info['描述'] = info.get('description')
        video_info['標籤'] = info.get('tags')
        video_info['網頁網址'] = info.get('webpage_url')
        video_info['上傳日期'] = info.get('upload_date')
    return video_info

def CheckFileInDrive(event, settings_path):
    parent = "1-GUcBDs9zeH9mwqkTMbwXiztv1QFJigR"
    gauth = GoogleAuth(settings_file=settings_path)
    drive = GoogleDrive(gauth)
    userName = GetPersonaName(event.source.user_id)
    FileWhetherExist = False
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for file1 in file_list:
        if (str(file1['title']) == userName):
            FileWhetherExist = True
            FolderId = file1['id']
            print(FolderId)
            return FolderId
            
    
    if (FileWhetherExist == False):
        folder_metadata = {
            'title' : userName,
            'mimeType' : 'application/vnd.google-apps.folder',
            "parents": [
                {
                    "kind": "drive#fileLink", 
                    "id": "1-GUcBDs9zeH9mwqkTMbwXiztv1QFJigR"
                }
            ]
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        return ListFolder("1-GUcBDs9zeH9mwqkTMbwXiztv1QFJigR", userName, settings_path)

def GetPersonaName(userid):
    URL = "https://api.line.me/v2/bot/profile/" + userid
    header = {'Authorization': 'Bearer ' + LineBotApiKey + "'"}
    ReturnRequests = requests.get(URL, headers = header)
    return str(ReturnRequests.json()['displayName'])

def ListFolder(parent, FolderId, settings_path):
    gauth = GoogleAuth(settings_file=settings_path)
    drive = GoogleDrive(gauth)
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for f in file_list:
        if (f['title'] == FolderId): # if folder
            return f['id']

def UploadFile(FolderId, FileName):
    for i in range(60):
        try:
            gauth = GoogleAuth(settings_file=settings_path)
            drive = GoogleDrive(gauth)
            file2 = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": FolderId}]})
            file2.SetContentFile(FileName)
            file2.Upload()
            return
        except Exception as InsertErrorMessage:
            print(InsertErrorMessage)
        time.sleep(5)

# def UploadFile(FolderId, FileName):
#     gauth = GoogleAuth(settings_file=settings_path)
#     drive = GoogleDrive(gauth)
#     file2 = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": FolderId}]})
#     file2.SetContentFile(FileName)
#     file2.Upload()

def SerachRegisterInDatabase(event):
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        cur.execute("SELECT * FROM lineregister WHERE userid = '" + event.source.user_id + "'")
        rows = cur.fetchall()
        if rows == []:
            SearchUserIdCheck = False
        else:
            SearchUserIdCheck = True
        conn.commit()
        cur.close()
        return SearchUserIdCheck
    except:
        SearchUserIdCheck = False
        return SearchUserIdCheck

def RegisterToDatabase(event):
    try:
        conn = psycopg2.connect(database=(config['PostgresSQL']['database']), user=(config['PostgresSQL']['user']), password=(
            config['PostgresSQL']['password']), host=(config['PostgresSQL']['host']), port=(config['PostgresSQL']['port']))
        cur = conn.cursor()
        UserName =  GetPersonaName(event.source.user_id)
        NowTime = datetime.today()
        NowTime_str = NowTime.strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO lineregister(username, userid, userregistertime) VALUES ('" + UserName + "', '" + str(event.source.user_id) + "', '" + NowTime_str + "')")
        conn.commit()
        cur.close()
        InsertSuccessMessage = UserName + "您好！\n\n您的會員編號為：" + str(event.source.user_id) + "，已新增成功！！，\n\n您可以開始使用此系統了！！"
        return InsertSuccessMessage
    except Exception as InsertErrorMessage:
        return str(InsertErrorMessage)

def StringProcess(title):
    replaceText = ['\\','/',':','*','?','"','<','>','|']
    for i in range(len(replaceText)):
        title = title.replace(replaceText[i], '')
    return title

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 1234))
    app.run(host='0.0.0.0', port=port)