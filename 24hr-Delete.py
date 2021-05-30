from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

settings_path = 'settings.yaml'

parent = "1-GUcBDs9zeH9mwqkTMbwXiztv1QFJigR"

def ListFolder(parent):
    gauth = GoogleAuth(settings_file=settings_path)
    drive = GoogleDrive(gauth)
    filelist=[]
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for f in file_list:
        if f['mimeType']=='application/vnd.google-apps.folder': # if folder
            f.Delete()
        else:
            filelist.append(f['title'])
    return filelist

ListFolder(parent)