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
config.read("./key/config.ini")
# LineBotApiKey = (config['LineToken_Youtube_dl']['LineBotApiKey'])
# WebhookHandlerKey = (config['LineToken_Youtube_dl']['WebhookHandler'])
settings_path = './key/Youtube_dl/settings.yaml'
# gauth = GoogleAuth(settings_file=settings_path)
# # gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)

# Channel Access Token
line_bot_api_Youtube_dl = LineBotApi(config['LineToken_Youtube_dl']['LineBotApiKey'])
# Channel Secret
handler_Youtube_dl = WebhookHandler(config['LineToken_Youtube_dl']['WebhookHandler'])

# Channel Access Token
line_bot_api_URL_Download = LineBotApi(config['LineToken_URL_Download']['LineBotApiKey'])
# Channel Secret
handler_URL_Download = WebhookHandler(config['LineToken_URL_Download']['WebhookHandler'])

@app.route('/')
def index():
    return "<p>Line Bot Connection To Ngrok Success!</p>"

# 監聽所有來自 /Youtube_dl/callback 的 Post Request
@app.route("/Youtube_dl/callback", methods=['POST'])
def youtube_dl_Callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler_Youtube_dl.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 監聽所有來自 /URL_Download/callback 的 Post Request
@app.route("/URL_Download/callback", methods=['POST'])
def url_Download_Callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler_URL_Download.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler_URL_Download.add(MessageEvent, message=TextMessage)
def handle_message_URL_Download(event):
    UserMessage = event.message.text
    try:
        if(UserMessage.split('/')[2].lower() == "risu.io"):
            image_message = ImageSendMessage(
                original_content_url='https://lh6.googleusercontent.com/YAfS0Rfed6WE6UG9Ed3q00oQI93f2zcHGxi6bP513R2DYzB2qqyrtco-PsEK6_-oYtU_AIDwIef5jr7OJFrg=w1920-h937',
                preview_image_url='https://lh6.googleusercontent.com/YAfS0Rfed6WE6UG9Ed3q00oQI93f2zcHGxi6bP513R2DYzB2qqyrtco-PsEK6_-oYtU_AIDwIef5jr7OJFrg=w1920-h937'
            )
            line_bot_api_URL_Download.reply_message(event.reply_token, image_message)
            # line_bot_api_URL_Download.reply_message(event.reply_token, TextSendMessage(text = "https://risu.io"))
        elif(UserMessage.split('/')[2].lower() == "ppt.cc"):
            line_bot_api_URL_Download.reply_message(event.reply_token, TextSendMessage(text = "https://ppt.cc"))
        elif(UserMessage.split('/')[2].lower() == "imgus.cc"):
            line_bot_api_URL_Download.reply_message(event.reply_token, TextSendMessage(text = "https://imgus.cc"))
        elif(UserMessage.split('/')[2].lower() == "lurl.cc"):
            line_bot_api_URL_Download.reply_message(event.reply_token, TextSendMessage(text = "https://lurl.cc"))
        elif(UserMessage.split('/')[2].lower() == "mork.ro"):
            line_bot_api_URL_Download.reply_message(event.reply_token, TextSendMessage(text = "https://mork.ro"))
        elif(UserMessage.split('/')[2].lower() == "myppt.cc"):
            line_bot_api_URL_Download.reply_message(event.reply_token, TextSendMessage(text = "https://myppt.cc"))
    except:
        pass
    # line_bot_api_URL_Download.reply_message(event.reply_token, TextSendMessage(text = UserMessage))

@handler_Youtube_dl.add(MessageEvent, message=TextMessage)
def handle_message_Youtube_dl(event):
    UserMessage = event.message.text
    CheckWhereRegister = SerachRegisterInDatabase(event)

    if (CheckWhereRegister == False):
        if (UserMessage.lower() == "register" or UserMessage.lower() == "註冊"):
            # 關閉註冊功能
            # Messages = "註冊時間開放至2021-06-04，目前不在開放時間內！\n\n有任何問題請洽開發人員！\n\n聯絡方式為使用條款網站內，下圖所示之地方：\n\n使用條款：https://reurl.cc/nonY0X"
            # image_map = "https://raw.githubusercontent.com/TsaiRongFu/Donwload-bot/main/image/StopRegisterFunction.png"
            # line_bot_api_Youtube_dl.reply_message(event.reply_token, [TextSendMessage(text= Messages), ImageSendMessage(original_content_url=image_map, preview_image_url=image_map)])
            # WriteLogFile(GetPersonaName(event.source.user_id) + " use regiser ， User_ID：" + event.source.user_id + " ， But now not register time." )
            # 開啟註冊功能
            Messages = RegisterToDatabase(event)
            line_bot_api_Youtube_dl.reply_message(event.reply_token, TextSendMessage(text = Messages))
            WriteLogFile(GetPersonaName(event.source.user_id) + " use regiser ， User_ID：" + event.source.user_id)
        elif (UserMessage == "使用說明" or UserMessage == "使用教學"):
            SendDescription(event)
            WriteLogFile(GetPersonaName(event.source.user_id) + " use " + UserMessage)
        else:    
            Messages = str(GetPersonaName(event.source.user_id))+ "" + "你好！\n\n目前此功能只提供給註冊用戶使用\n\n目前開放註冊到2021-06-04\n\n如您需要註冊請輸入：Register"
            line_bot_api_Youtube_dl.reply_message(event.reply_token, TextSendMessage(text = Messages))
            WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage)
    elif (CheckWhereRegister == True):
        if (UserMessage.lower() == "register" or UserMessage.lower() == "註冊"):
            Messages = str(GetPersonaName(event.source.user_id)) + "，您已經註冊過了！\n\n使用前還請再次詳閱使用條款\nhttps://reurl.cc/nonY0X\n\n使用過程中有任何問題請洽開發人員網站提出Issues\nhttps://git.io/Donwload-Bot\n\n使用範例如下：\n\n如果要下載影片請輸入:mp4-影片網址\n\n如果要音樂影片請輸入:mp3-音樂網址"
            line_bot_api_Youtube_dl.reply_message(event.reply_token, TextSendMessage(text = Messages))
            WriteLogFile(GetPersonaName(event.source.user_id) + " send \"" + UserMessage + "\" but user already register")
        elif (UserMessage == "使用說明" or UserMessage == "使用教學"):
            SendDescription(event)
            WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage)
        elif ((UserMessage.split("-")[0]).lower() == "mp3" or UserMessage.split("-")[0] == "音樂"):
            try:
                video_info = get_video_info(UserMessage.split("-", 1)[1])
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
                    ydl.download([UserMessage.split("-", 1)[1]])
                    Messages = FileName + "，下載完畢！\n\n正在上傳(依照檔案大小所需時間不同)，稍後可以在以下網址，您的資料夾內找到檔案！\n\nhttps://tinyurl.com/3vr8fus3"
                    FolderId = CheckFileInDrive(event,settings_path)
                    WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage + "，" + FileName + " 下載完成！")
                    # UploadFile(FolderId, str(StringProcess(str(video_info['標題']))) + ".mp3")
                    t = threading.Thread(target = UploadFileMp3, args = (FolderId, str(StringProcess(str(video_info['標題']))) + ".mp3", event, UserMessage))
                    t.start()
            except Exception as InsertErrorMessage:
                WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage + "but system error ，Error messages ：\"" + str(InsertErrorMessage))
                Messages = str(InsertErrorMessage)
            line_bot_api_Youtube_dl.reply_message(event.reply_token, TextSendMessage(text = Messages))
        elif ((UserMessage.split("-")[0]).lower() == "mp4" or UserMessage.split("-")[0] == "影片"):
            try:
                video_info = get_video_info(UserMessage.split("-", 1)[1])
                ydl_opts_mp4 = {
                    'outtmpl': StringProcess(str(video_info['標題'])) + ".mp4",
                    'format': "bestvideo[ext=mp4]+bestaudio/best",
                    'logger': MyLogger(),
                    'progress_hooks': [my_hook],
                }
                FileName = str(video_info['標題'])
                with youtube_dl.YoutubeDL(ydl_opts_mp4) as ydl:
                    ydl.download([UserMessage.split("-", 1)[1]])
                    Messages = FileName + "，下載完畢！\n\n正在上傳(依照檔案大小所需時間不同)，稍後可以在以下網址，您的資料夾內找到檔案！\n\nhttps://tinyurl.com/3vr8fus3"
                    FolderId = CheckFileInDrive(event,settings_path)
                    WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage + "，" + FileName + " 下載完成！")
                    # UploadFile(FolderId, str(StringProcess(str(video_info['標題']))) + ".mp4")
                    t = threading.Thread(target = UploadFileMp4, args = (FolderId, str(StringProcess(str(video_info['標題']))), event, UserMessage))
                    t.start()
            except Exception as InsertErrorMessage:
                WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage + "but system error ，Error messages" + str(InsertErrorMessage))
                Messages = str(InsertErrorMessage)
            line_bot_api_Youtube_dl.reply_message(event.reply_token, TextSendMessage(text = Messages))
        else:
            Messages = "請輸入正確格式！\n\n如果您忘記指令請輸入 \"使用教學\""
            line_bot_api_Youtube_dl.reply_message(event.reply_token, TextSendMessage(text = Messages))
            WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage)
    else:
        Messages = "請輸入正確格式！\n\n如果您忘記指令請輸入 \"使用教學\""
        line_bot_api_Youtube_dl.reply_message(event.reply_token, TextSendMessage(text = Messages))
        WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage)

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
    header = {'Authorization': 'Bearer ' + config['LineToken_Youtube_dl']['LineBotApiKey'] + "'"}
    ReturnRequests = requests.get(URL, headers = header)
    UserName = str(ReturnRequests.json()['displayName'])
    return UserName

def ListFolder(parent, FolderId, settings_path):
    gauth = GoogleAuth(settings_file=settings_path)
    drive = GoogleDrive(gauth)
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for f in file_list:
        if (f['title'] == FolderId): # if folder
            return f['id']

def UploadFileMp4(FolderId, FileName, event, UserMessage):
    for i in range(60):
        try:
            gauth = GoogleAuth(settings_file = settings_path)
            drive = GoogleDrive(gauth)
            file2 = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": FolderId}]})
            file2.SetContentFile(FileName + ".mp4")
            file2.Upload()
            WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage + "，" + FileName + " 上傳成功！！")
            return
        except:
            try:
                gauth = GoogleAuth(settings_file = settings_path)
                drive = GoogleDrive(gauth)
                file2 = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": FolderId}]})
                file2.SetContentFile(FileName + ".mkv")
                file2.Upload()
                WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage + "，" + FileName + " 上傳成功！！")
                return
            except Exception as MKVErrorMessage:
                WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage + "but system error ，Error Messages ：\"" + str(MKVErrorMessage) + "\"")
                print(MKVErrorMessage)
        time.sleep(5)

def UploadFileMp3(FolderId, FileName, event, UserMessage):
    for i in range(60):
        try:
            gauth = GoogleAuth(settings_file = settings_path)
            drive = GoogleDrive(gauth)
            file2 = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": FolderId}]})
            file2.SetContentFile(FileName)
            file2.Upload()
            WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage + "，" + FileName + " 上傳成功！！")
            return
        except Exception as ErrorMessage:
            WriteLogFile(GetPersonaName(event.source.user_id) + " send " + UserMessage + "but system error ，Error Messages ：\"" + str(ErrorMessage) + "\"")
            print(ErrorMessage)
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
        InsertSuccessMessage = UserName + "您好！\n\n您的會員編號為：" + str(event.source.user_id) + "\n\n已註冊成功！！\n\n使用前還請再次詳閱使用條款\nhttps://reurl.cc/Gmdkrd\n\n使用過程中有任何問題請洽開發人員網站提出Issues\nhttps://git.io/Donwload-Bot\n\n您可以開始使用此系統了！！"
        return InsertSuccessMessage
    except Exception as InsertErrorMessage:
        return str(InsertErrorMessage)

def StringProcess(title):
    replaceText = ['\\','/',':','*','?','"','<','>','|']
    for i in range(len(replaceText)):
        title = title.replace(replaceText[i], '')
    return title

def SendDescription(event):
    Messages1 = "如果要下載影片請輸入:mp4-影片網址\n\n如果要音樂影片請輸入:mp3-音樂網址"
    Messages2 = "範例一 音樂下載\n\nmp3-https://www.youtube.com/watch?v=Sv0OblpjrOw"
    Messages3 = "範例二 影片下載\n\nmp4-https://www.youtube.com/watch?v=Sv0OblpjrOw"
    image_map = ["https://raw.githubusercontent.com/TsaiRongFu/Video-Donwload-bot/main/image/mp3.jpg", "https://raw.githubusercontent.com/TsaiRongFu/Video-Donwload-bot/main/image/mp4.jpg"]
    line_bot_api_Youtube_dl.reply_message(event.reply_token, [TextSendMessage(text= Messages1), TextSendMessage(text= Messages2), ImageSendMessage(original_content_url=image_map[0], preview_image_url=image_map[0]), TextSendMessage(text= Messages3), ImageSendMessage(original_content_url=image_map[1], preview_image_url=image_map[1])])

def WriteLogFile(content):
    NowTime = datetime.today()
    NowTime_str = NowTime.strftime("%Y-%m-%d %H:%M:%S")
    LogFile = open("./log/UserUselog.txt", 'a', encoding='utf-8')
    LogFile.write("\n[" + NowTime_str + "]" + " " + str(content))
    LogFile.close()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 6969))
    app.run(host='0.0.0.0', port=port)