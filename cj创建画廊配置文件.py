
import json
import os
import shutil

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

def saveJS(object, saveFilePath):
    with open(saveFilePath, "w", encoding='utf-8') as f:
        f.write('var data = '+json.dumps(object,indent=4, ensure_ascii=True)+";")


data = dict()

for file in print_files(r"./"):
    path,name = os.path.split(file)
    if(name == '.ehviewer'):
        gInfo = dict()
        gInfo['path'] = path
        gInfo['GallaryName'] = path.split('/')[-1]
        with open(os.path.join(r'./json/', gInfo['GallaryName']+".json") , 'r') as f:
            jsonFile = json.load(f)
            gInfo['tags'] = dict()
            for row in ['artist', 'character', 'female', 'group', 'language', 'male', 'misc', 'parody', 'reclass']:
                gInfo['tags'][row] = jsonFile[row]
            data[jsonFile['gid']+'_'+jsonFile['token']] = gInfo

            profitJS = dict()
            fileList = []
            for singFile in print_files(path):
                if(os.path.splitext(os.path.split(singFile)[1])[1] in [".JPG", ".jpg", ".PNG", ".png", ".jpeg", ".JPEG", ".GIF", ".gif"]):
                    fileList.append(os.path.split(singFile)[1])
            fileList.sort()
            profitJS = dict()
            profitJS['pics'] = fileList
            profitJS['info'] = jsonFile
            saveJS(profitJS,os.path.join(path,'profile.js'))
            shutil.copyfile(os.path.join(path, fileList[0]), os.path.join(r'./cover/', jsonFile['gid']+'_'+jsonFile['token']+'.jpg'))

saveJS(data,r'./data.js')
