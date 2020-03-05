import urllib.request
import pickle
import re
import os
import urllib.parse as parse
import time
import vthread
from urllib import error
import json


def print_files(path):
    fileList = []
    lsdir = os.listdir(path)
    dirs = [i for i in lsdir if os.path.isdir(os.path.join(path, i))]
    if dirs:
        for i in dirs:
            fileList += (print_files(os.path.join(path, i)))
    files = [i for i in lsdir if os.path.isfile(os.path.join(path, i))]
    count = 0
    for f in files:
        fileList.append(os.path.join(path, f))
    return fileList


def getHTML(url):
    try:
        getUrl = url
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Cookie': "__cfduid=****;event=****;ipb_member_id=****;ipb_pass_hash=****;ipb_session_id=****;s=***;sk=****"
        }  # COOKIE插件直接获取 这里仅做展示
        req = urllib.request.Request(url=getUrl, headers=headers)
        res = urllib.request.urlopen(req)
        html = res.read().decode('utf-8')
        return html
    except error.URLError as e:
        return None  # 获取网页错误


def saveJSON(FilePath, object):
    with open(FilePath, "w", encoding='utf-8') as f:
        f.write(json.dumps(object, indent=4, ensure_ascii=False))


@vthread.pool(20)
def solution(f):
    path, name = os.path.split(f)
    gallaryname = path.split('/')[-1]
    jsFile = "./json/"+gallaryname+".json"
    if(os.path.exists(jsFile)):
        return
    save_to_json = dict()
    save_to_json['fileName'] = gallaryname
    save_to_json['gallaryName'] = ''
    save_to_json['gid'] = ''
    save_to_json['token'] = ''
    save_to_json['artist'] = []
    save_to_json['character'] = []
    save_to_json['female'] = []
    save_to_json['group'] = []
    save_to_json['language'] = []
    save_to_json['male'] = []
    save_to_json['misc'] = []
    save_to_json['parody'] = []
    save_to_json['reclass'] = []

    with open(f, 'r') as f:
        test = f.read(-1)
        gidToken = test.split('\n')
        gidToken = gidToken[2]+"/"+gidToken[3]
        url = r'https://exhentai.org/g/'+gidToken
        save_to_json['gid'], save_to_json['token'] = gidToken.split("/")
        htmlText = getHTML(url)
        if(htmlText is not None):
            pattern = r'<h1 id="gj">[^<]+</h1>'
            result = re.findall(pattern, htmlText)
            if(len(result) == 0):
                pattern = r'<h1 id="gn">[^<]+</h1>'
                result = re.findall(pattern, htmlText)
            save_to_json['gallaryName'] = result[0][12:-5]

            pattern = r"toggle_tagmenu\('[^:]*:[^']*',this\)"
            result = re.findall(pattern, htmlText)
            print(gallaryname)
            print(url)
            print(save_to_json['gallaryName'])
            for tag in result:
                if(":" in tag):
                    row, data = tag[16:-7].split(":")
                    save_to_json[row].append(data)
                    print(row, data)
            print()
            saveJSON("./json/"+gallaryname+".json", save_to_json)
        else:
            print("URL_REQ_ERROR")
            return


if __name__ == "__main__":

    fileList = []

    if(not os.path.exists("./json/")):
        os.makedirs("./json/")

    for f in print_files('./'):
        path, name = os.path.split(f)
        if("ehviewer" in name):
            solution(f)
            fileList.append(os.path.split(f)[0].split('/')[-1])

    for f in print_files("./json/"):
        path, name = os.path.split(f)
        if(name[:-5] not in fileList):
            print("删除的画廊", f)
            os.remove(f)

    for f in print_files('./'):
        path, name = os.path.split(f)
        if('00000001.jpg' == name):
            gname = path.split('/')[-1]
            if (not os.path.exists('./json/'+gname+'.json')):
                print('没有找到.ehviewer文件', gname)
