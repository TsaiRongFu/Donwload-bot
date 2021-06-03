from os import listdir
from os.path import isfile, isdir, join
import os
from datetime import datetime

def WriteLogFile(content):
    NowTime = datetime.today()
    NowTime_str = NowTime.strftime("%Y-%m-%d %H:%M:%S")
    LogFile = open("./log/DeleteServerFileLog.txt", 'a', encoding='utf-8')
    LogFile.write("\n[" + NowTime_str + "]" + " " + str(content))
    LogFile.close()

mypath = "./"

files = listdir(mypath)

suffix = ["mp3","mp4","mkv"]

DeleteFileNameList = []

LogMessage = ""

for f in files:
    for i in range(len(suffix)):
        if f.endswith(suffix[i]):
            print("檔案：", f)
            os.remove(f)
            print(f + "，檔案刪除成功！")
            DeleteFileNameList.append(f)

if len(DeleteFileNameList)==0:
    content = "系統執行Delete，未檢測出可刪除檔案！"
    WriteLogFile(content)
    print("陣列為空！")
else:
    content = "系統執行Delete："
    for j in range (len(DeleteFileNameList)):
        if (j == 0):
            content += DeleteFileNameList[j]
        else:
            content += "、" + DeleteFileNameList[j]
        print(DeleteFileNameList[j])
        
    WriteLogFile(content)
    