#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import base64
import json
import shutil
from bottle import *


def readJS(saveFilePath):
    with open(saveFilePath, 'r', encoding='utf-8') as f:
        text = f.read(-1)
        object = json.loads(text[11:-1])
        return object


def saveJS(object, saveFilePath):
    with open(saveFilePath, "w", encoding='utf-8') as f:
        f.write('var data = '+json.dumps(object,
                                         indent=4, ensure_ascii=True)+";")


workPath = r"D:\waterFallDemo"

gallaryData = readJS(os.path.join(workPath, "data.js"))


@route('/')
def index():
    return static_file('managePage.html', root=workPath)


@route('/deleteGallarys', method='POST')
def deleteGallarys():
    data = request.body.read()
    args = None
    try:
        args = json.loads(data.decode("utf-8"))
    except Exception as e:
        return "JSON格式错误"
    print(args)
    result = {}
    for value in args:
        if value in gallaryData:
            path = gallaryData[value]['path']  # 画廊路径
            shutil.move(os.path.join(workPath, path), os.path.join(os.path.join(
                workPath, r"deleted"), path))  # 移动画廊而不是删除
            os.remove(os.path.join(os.path.join(
                workPath, r'cover'), value+".jpg"))  # 封面
            gallaryData.pop(value)  # data.js中删除
            result[value] = "success"
        else:
            result[value] = "failed"
    saveJS(gallaryData, os.path.join(workPath, "data.js"))  # 保存
    return json.dumps(result)


@route('/<path:path>')
def server_post(path):
    print("["+path+"]")
    return static_file(path, root=workPath)


try:
    run(host='localhost', port=8080, reloader=False)
except (KeyboardInterrupt):
    exit()
