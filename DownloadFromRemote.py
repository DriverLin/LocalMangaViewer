#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import queue
import shutil
import math
import urllib.parse as parse
import urllib.request
import requests
from urllib import error
from urllib.request import quote
from PIL import Image, ImageSequence
import re
import vthread


def readJS(saveFilePath):
    with open(saveFilePath, 'r', encoding='utf-8') as f:
        text = f.read(-1)
        object = json.loads(text[11:-1])
        return object


def saveJS(object, saveFilePath):
    with open(saveFilePath, "w", encoding='utf-8') as f:
        f.write('var data = '+json.dumps(object,
                                         indent=4, ensure_ascii=True)+";")


def reqUrl(getUrl):
    try:
        req = urllib.request.Request(url=getUrl)
        res = urllib.request.urlopen(req)
        data = res.read().decode('utf-8')
        return data
    except:
        downloadLog.append("Error:\treqUrlError:\t"+getUrl)
        return "ERROR-HTTP error"  # 获取网页错误


def convertCover(FilePath):
    try:
        img = Image.open(FilePath)
        if(img.format == "GIF"):  # GIF
            img = ImageSequence.Iterator(img)[0]
        img = img.convert('RGB')
        w, h = img.size
        img = img.resize((780,  int(780 / w * h)))
        # 远端创建的画廊的封面也是统一JPG
        # GIF,PNG也只是修改后缀名 没有调整大小
        # 所以下载下来的也只有JPG后缀的
        img.save(FilePath)
    except Exception as e:
        print(FilePath + '封面转换失败:' + e.__str__())


def updateDataVersion(waitingForUpdate):
    html = open(waitingForUpdate, 'r', encoding='utf-8').read()
    pattern = re.compile(r'<script src="./Data.js\?ver=\d+"></script>')
    result = pattern.findall(html)
    newVersion = str(int(result[0][27:-11])+1)
    newDatajs = '<script src="./Data.js?ver={}"></script>'.format(newVersion)
    print(newDatajs)
    newHtml = re.sub(
        r'<script src="./Data.js\?ver=\d+"></script>', newDatajs, html)
    with open(waitingForUpdate, 'w', encoding='utf-8') as f:
        f.write(newHtml)


threadQueue = queue.Queue()
@vthread.pool(8)
def downloadFile(url, path):  # 保证文件存储目录存在 先计数 再下载
    if (os.path.exists(path)):  # 文件存在
        downloadLog.append("Warning:\tfielExisted:\t" + path)
    try:
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req)
        data = res.read()
        with open(path, 'wb') as f:
            f.write(data)
        # log.append("Record:\tdownloadFileError:\t"+url+"->"+path)
        threadQueue.put(None)
    except:
        downloadLog.append("Error:\tdownloadFileError:\t"+url+"->"+path)
        threadQueue.put(None)


def checkCompleteness(gallarypath):
    profilePath = os.path.join(gallarypath, "profile.js")
    if not os.path.exists(profilePath):
        return False
    profile = readJS(profilePath)
    for pic in profile['pics']:
        if not os.path.exists(os.path.join(gallarypath, pic)):
            return False
    return True


def downloadGarralry(GID_TOKEN):
    if GID_TOKEN in localData:
        print("本地已存在 pass\n")
        return
    remotePath = quote(gallaryData[GID_TOKEN]['path'][2:])  # 远程文件路路径
    profileJs = parse.urljoin(root, remotePath+"/profile.js")
    profileJs = reqUrl(profileJs)
    if (profileJs != "ERROR-HTTP error"):
        profile = json.loads(profileJs[11:-1])  # profile配置文件
        saveDir = os.path.join(downloadGallaryPath,
                               profile['info']['fileName'])
        if (not os.path.exists(saveDir)):  # 创建目录
            os.makedirs(saveDir)
        else:
            if checkCompleteness(saveDir):  # 如果检查完整性通过了 就跳过 否则下载
                print('下载已完成 pass\n')  # 可能是下载终止
                return
        for picture in profile['pics']:
            pictureUrl = parse.urljoin(
                root, remotePath + "/" + picture)
            savePath = os.path.join(os.path.join(
                downloadGallaryPath, profile['info']['fileName']), picture)  # gallarySavePath + filename + picture
            downloadFile(pictureUrl, savePath)

        for i in range(len(profile['pics'])):
            threadQueue.get()
            barLength = 100
            finishedPart = math.ceil((i+1)*barLength/len(profile['pics']))
            print("["+"■"*finishedPart +
                  "□" * (barLength-finishedPart)+"]"+str(i+1)+"/"+str(len(profile['pics'])), end="\r")
        print("\n")
        with open(os.path.join(os.path.join(downloadGallaryPath, profile['info']['fileName']), "profile.js"), 'w') as f:
            f.write(profileJs)
        downloadFile(parse.urljoin(root, "/cover/"+GID_TOKEN+".jpg"),
                     os.path.join(downloadCoverPath, GID_TOKEN + ".jpg"))  # 下载封面)
        threadQueue.get()  # 封面下载完毕
        convertCover(os.path.join(downloadCoverPath,
                                  GID_TOKEN + ".jpg"))  # 转换格式

    else:
        print("profileJsReadError")
        return


def checkDownloadCompleted():
    print("读取中")
    dirs = os.listdir(downloadGallaryPath)
    print('画廊总数:'+str(len(dirs)))
    lenOfDirs = len(dirs)
    count = 0
    for cdir in dirs:
        cpath = os.path.join(downloadGallaryPath, cdir)
        if not checkCompleteness(cpath):
            print(cpath, '出错')
            return False
        count += 1
        print('画廊检查中:'+str(count)+'/'+str(lenOfDirs) +
              '\t', end='\r')

    print('\n完成')
    return True


def mergeGallery(localData):
    mergeLog = ''
    print('添加新画廊')
    fileList = []
    lsdir = os.listdir(downloadGallaryPath)
    dirs = [i for i in lsdir if os.path.isdir(
        os.path.join(downloadGallaryPath, i))]
    newData = dict()
    if len(dirs) != 0:
        count = 0
        lenOfDirs = len(dirs)
        for i in dirs:
            gallary = dict()
            gallarydir = os.path.join(downloadGallaryPath, i)
            profile = readJS(os.path.join(
                gallarydir, r"profile.js"))
            fileName = profile['info']['fileName']
            gid = profile['info']['gid']
            token = profile['info']['token']
            key = gid + "_" + token
            gallary["path"] = gallarydir.replace(
                downloadGallaryPath, r".\Gallarys", 1)
            gallary["GallaryName"] = profile['info']['gallaryName']
            gallary['tags'] = dict()
            for row in ['artist', 'character', 'female', 'group', 'language', 'male', 'misc', 'parody', 'reclass']:
                gallary['tags'][row] = profile['info'][row]
            newData[key] = gallary
            count += 1
            print(" 读取中:"+str(count)+"/"+str(lenOfDirs), end='\r')
    print('\n完毕')

    oldGallarys = [key for key in newData if key in localData]
    if oldGallarys:
        print("正在删除旧版本画廊")
        count = 0
        lenOfOldGallarys = len(oldGallarys)
        for key in oldGallarys:
            gPath = os.path.join(
                localGallaryPath, localData[key]['path'].split('\\')[-1])  # 画廊路径
            print(gPath)
            pPath = os.path.join(localCoverPath, key+'.jpg')
            print(pPath)
            shutil.rmtree(gPath)
            shutil.remove(pPath)
            mergeLog += '删除目录' + gPath + '\n'
            mergeLog += '删除文件' + pPath + '\n'
            localData.pop(key)  # data.js中删除
            count += 1
            print(" 删除中:"+str(count)+"/" +
                  str(lenOfOldGallarys), end='\r')
        print('\n完毕')

    count = 0
    lenOfnewData = len(newData)
    for key in newData:
        localData[key] = newData[key]
        originalPath = os.path.join(
            downloadGallaryPath, localData[key]['path'].split('\\')[-1])
        targetPath = os.path.join(
            localGallaryPath, localData[key]['path'].split('\\')[-1])
        shutil.move(originalPath, targetPath)
        shutil.move(os.path.join(downloadCoverPath, key+'.jpg'),
                    os.path.join(localCoverPath, key+'.jpg'))
        mergeLog += '移动' + originalPath + '->' + targetPath + '\n'
        count += 1
        print(" 合并中:"+str(count)+"/"+str(lenOfnewData), end='\r')
    saveJS(localData, localDataJsPath)
    updateDataVersion(indexPath)
    updateDataVersion(viewPath)
    with open(mergeLogFile, 'w', encoding='utf-8') as f:
        f.write(mergeLog)
    print('完成')


def addFavorites(gallaryData):
    @vthread.pool(5)
    def post_addFaov(g, t):
        url = "https://exhentai.org/gallerypopups.php?gid={}&t={}&act=addfav".format(
            g, t)
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Length": "49",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "ipb_member_id=3245653; ipb_pass_hash=e82ccb4be395b8727bc0910ff1005d77; igneous=ccb85f96e; sl=dm_1; sk=5nk0h6ihbfmq7ro14bnjcbofgpwm; s=342107113",
            "DNT": "1",
            "Host": "exhentai.org",
            "Origin": "https://exhentai.org",
            "Referer": "https://exhentai.org/gallerypopups.php?gid=1689016&t=51caf6a963&act=addfav",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.39"
        }
        payload = "favcat=9&favnote=&apply=Add+to+Favorites&update=1".encode(
            "utf-8")
        try:
            r = requests.post(url, data=payload, headers=headers)
            print(r)
        except Exception as e:
            print("error"+str(e))
        finally:
            tasks.task_done()
    tasks = queue.Queue()
    for key in gallaryData:
        g, t = key.split("_")
        tasks.put(key)
        post_addFaov(g, t)
    tasks.join()


root = 'http://192.168.137.151:8000/'
# root = 'http://127.0.0.1:7964/'
workPath = r"D:\waterFallDemo"

downloadGallaryPath = os.path.join(workPath, r"DownloadFromRemote\gallarys")
downloadCoverPath = os.path.join(workPath, r"DownloadFromRemote\cover")
downloadLogFilePath = os.path.join(workPath, r"DownloadFromRemote\log.txt")
localDataJsPath = os.path.join(workPath, r"Data.js")
localGallaryPath = os.path.join(workPath, r"Gallarys")
localCoverPath = os.path.join(workPath, r"cover")
mergeLogFile = os.path.join(workPath, r"MergeLog.log")
indexPath = os.path.join(workPath, r"index.html")
viewPath = os.path.join(workPath, r"viewing.html")
downloadLog = []
localData = None

if __name__ == '__main__':
    localData = readJS(localDataJsPath)
    if (not os.path.exists(downloadGallaryPath)):
        os.makedirs(downloadGallaryPath)
    if (not os.path.exists(downloadCoverPath)):
        os.makedirs(downloadCoverPath)
    dataJs = reqUrl(parse.urljoin(root, "data.js"))
    if (dataJs != "ERROR-HTTP error"):
        gallaryData = json.loads(dataJs[11:-1])
        print('远程画廊总数:'+str(len(gallaryData)))
        for existedGallery in localData:
            if existedGallery in gallaryData:
                gallaryData.pop(existedGallery)
        print('本地不存在的共:'+str(len(gallaryData)))
    else:
        print("Error:\tdata.js read failed")
        exit(1)
    count = 0
    total = len(gallaryData)
    for key in gallaryData:
        count = count + 1
        downloadLog.append("Record:\tdownloadGallary:\t"+key+"->" +
                           gallaryData[key]["GallaryName"])
        print(key, "  ["+str(count)+" of "+str(total)+"]")
        downloadGarralry(key)  # 下载画廊
    with open(downloadLogFilePath, 'w', encoding='utf-8') as f:
        for line in downloadLog:
            f.write(line+"\n")

    options = input("是否检查完整性？ y/n")
    while options not in ['', 'y', 'n', 'Y', 'n', 'YES', 'NO', 'yes', 'no']:
        options = input("是否检查完整性？ y/n")
    if options in ['', 'y', 'Y', 'YES', 'yes']:
        checkResult = checkDownloadCompleted()
        if checkResult:  # 下载无误
            options = input("是否添加收藏？ y/n")  # 收藏添加失败 则可以手动选择是否继续合并
            while options not in ['', 'y', 'n', 'Y', 'n', 'YES', 'NO', 'yes', 'no']:
                options = input("是否添加收藏？ y/n")
            if options in ['', 'y', 'Y', 'YES', 'yes']:
                addFavorites(gallaryData)
            options = input("下载完整性检查完毕，是否执行合并？y/n")
            while options not in ['', 'y', 'n', 'Y', 'n', 'YES', 'NO', 'yes', 'no']:
                options = input("下载完整性检查完毕，是否执行合并？y/n")
            if options in ['', 'y', 'Y', 'YES', 'yes']:
                mergeGallery(localData)
