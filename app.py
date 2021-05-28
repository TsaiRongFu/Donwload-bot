from __future__ import unicode_literals
import os
from flask import Flask, request, abort, send_file
from pytz import utc, timezone
from datetime import datetime
import configparser  # 匯入config套件
import requests
import youtube_dl
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import time

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

# 處理訊息


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    UserMessage = event.message.text    
    # p = subprocess.Popen('ls',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.read()
    if (UserMessage.split("-")[0] == "mp3" or UserMessage.split("-")[0] == "音樂"):
        ydl_opts_mp3 = {
            'format': "bestaudio/best",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }
        try:
            video_info = get_video_info(UserMessage.split("-")[1])
            FileName = str(video_info['標題']) + "-" + str(video_info['ID'])
            with youtube_dl.YoutubeDL(ydl_opts_mp3) as ydl:
                ydl.download([UserMessage.split("-")[1]])
                Messages = FileName + "，下載完畢！\n\n正在上傳，稍後可以在以下網址，您的資料夾內找到檔案！\n\nhttps://tinyurl.com/3vr8fus3"
                FolderId = CheckFileInDrive(event,settings_path)
                UploadFile(FolderId,str(video_info['標題']) + "-" + str(video_info['ID']) + ".mp3")
        except Exception as InsertErrorMessage:
            Messages = str(InsertErrorMessage)
    elif (UserMessage.split("-")[0] == "mp4" or UserMessage.split("-")[0] == "影片"):
        ydl_opts_mp4 = {
            'format': "bestvideo[ext=mp4]+bestaudio/best",
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }
        try:
            video_info = get_video_info(UserMessage.split("-")[1])
            FileName = str(video_info['標題']) + "-" + str(video_info['ID'])
            with youtube_dl.YoutubeDL(ydl_opts_mp4) as ydl:
                ydl.download([UserMessage.split("-")[1]])
                Messages = FileName + "，下載完畢！\n\n正在上傳，稍後可以在以下網址，您的資料夾內找到檔案！\n\nhttps://tinyurl.com/3vr8fus3"
                FolderId = CheckFileInDrive(event,settings_path)
                UploadFile(FolderId,str(video_info['標題']) + "-" + str(video_info['ID']) + ".mp4")
        except Exception as InsertErrorMessage:
            Messages = str(InsertErrorMessage)
    else:
        # Messages = str(get_video_info(UserMessage))
        Messages = UserMessage
    # Messages = str(CheckFileInDrive(event,settings_path))
    
    

    # folder = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": "1-GUcBDs9zeH9mwqkTMbwXiztv1QFJigR"}]})
    # folder_metadata = {
    #     'title' : 'test',
    #     # The mimetype defines this new file as a folder, so don't change this.
    #     'mimeType' : 'application/vnd.google-apps.folder',
    #     "parents": [
    #         {
    #             "kind": "drive#fileLink", 
    #             "id": "1-GUcBDs9zeH9mwqkTMbwXiztv1QFJigR"
    #         }
    #     ]
    # }
    # folder = drive.CreateFile(folder_metadata)
    # folder.Upload()

    
    # parent = "1-GUcBDs9zeH9mwqkTMbwXiztv1QFJigR"

    # def ListFolder(parent):
    #     filelist=[]
    #     file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    #     for f in file_list:
    #         if f['mimeType']=='application/vnd.google-apps.folder': # if folder
    #             filelist.append({"id":f['id'],"title":f['title'],"list":ListFolder(f['id'])})
    #         else:
    #             filelist.append(f['title'])
    #     return filelist

    # print(ListFolder(parent))

    # file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
    # for file1 in file_list:
    #     print('title: {}, id: {}'.format(file1['title'], file1['id']))
    # Messages = str(CheckFileInDrive(event,settings_path))

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
    gauth = GoogleAuth(settings_file=settings_path)
    drive = GoogleDrive(gauth)
    userName = GetPersonaName(event.source.user_id)
    FileWhetherExist = False
    file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
    for file1 in file_list:
        if (str(file1['title']) == userName):
            FileWhetherExist = True
            FolderId = file1['id']
            return FolderId
        # print('title: {}, id: {}'.format(file1['title'], file1['id']))
    
    if (FileWhetherExist == False):
        folder_metadata = {
            'title' : userName,
            # The mimetype defines this new file as a folder, so don't change this.
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
    gauth = GoogleAuth(settings_file=settings_path)
    drive = GoogleDrive(gauth)
    file2 = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": FolderId}]})
    file2.SetContentFile(FileName)
    file2.Upload()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 1234))
    app.run(host='0.0.0.0', port=port)
    # ssl_context=('cert.pem', 'key.pem')