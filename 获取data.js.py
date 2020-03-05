
import json
import os
import shutil


dirpath = r'.\Gallarys'  # Gallarys文件夹
savePath = r'.\new_data.js'  # 输出文件


def readJS(saveFilePath):
    with open(saveFilePath, 'r', encoding='utf-8') as f:
        text = f.read(-1)
        object = json.loads(text[11:-1])
        return object


def saveJS(object, saveFilePath):
    with open(saveFilePath, "w", encoding='utf-8') as f:
        f.write('var data = '+json.dumps(object,
                                         indent=4, ensure_ascii=True)+";")


fileList = []
lsdir = os.listdir(dirpath)
dirs = [i for i in lsdir if os.path.isdir(os.path.join(dirpath, i))]

data = dict()
if dirs:
    for i in dirs:
        gallary = dict()
        gallarydir = os.path.join(dirpath, i)
        profile = readJS(os.path.join(gallarydir, r"profile.js"))
        fileName = profile['info']['fileName']
        gid = profile['info']['gid']
        token = profile['info']['token']
        key = gid + "_" + token
        gallary["path"] = gallarydir.replace(r'D:\waterFallDemo', ".", 1)
        gallary["GallaryName"] = profile['info']['gallaryName']
        gallary['tags'] = dict()
        for row in ['artist', 'character', 'female', 'group', 'language', 'male', 'misc', 'parody', 'reclass']:
            gallary['tags'][row] = profile['info'][row]
        data[key] = gallary

saveJS(data, savePath)
