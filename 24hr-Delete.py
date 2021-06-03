from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime

settings_path = './key/settings.yaml'

parent = "1-GUcBDs9zeH9mwqkTMbwXiztv1QFJigR"

def WriteLogFile(content):
    NowTime = datetime.today()
    NowTime_str = NowTime.strftime("%Y-%m-%d %H:%M:%S")
    LogFile = open("./log/DeleteGoogleDriveFileLog.txt", 'a', encoding='utf-8')
    LogFile.write("\n[" + NowTime_str + "]" + " " + str(content))
    LogFile.close()

def ListFolder(parent):
    gauth = GoogleAuth(settings_file=settings_path)
    drive = GoogleDrive(gauth)
    filelist=[]
    content = "系統執行Delete"
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for f in file_list:
        if f['mimeType']=='application/vnd.google-apps.folder': # if folder
            filelist.append(f['title'])
            content = content + " 刪除：" + f['title'] + "資料夾"
            f.Delete()
        else:
            pass
    if (len(filelist) == 0):
        content = "系統執行Delete，未檢測出可刪除檔案！"
    WriteLogFile(content)
    return filelist

ListFolder(parent)
