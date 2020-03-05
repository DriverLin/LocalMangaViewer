#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import base64
import json
from bottle import *


@route('/userLoginIn', method='POST')
def login():
    data = json.loads(request.body.read())
    print(data)
    if (data.get('password') == "12$%^&*789asdfghjkl"):
        response.set_cookie("key", "6sr4h5g135w4ysr9y8q")
        return ""
    else:
        return HTTPResponse(status=401)


@route('/index')
def index():
    if ("key" in request.cookies.keys()):
        key = request.cookies.get("key")
        if (key == "6sr4h5g135w4ysr9y8q"):
            return static_file('index.html', root='./')
    else:
        return "error"


@route('/login')
def login():
    return static_file('login.html', root='./')


@route("/")
def root():
    if ("key" in request.cookies.keys()):
        key = request.cookies.get("key")
        if (key == "6sr4h5g135w4ysr9y8q"):
            redirect('/index')
    else:
        redirect('/login')


@route('/<path:path>')
def server_post(path):
    print("["+path+"]")
    if ("key" in request.cookies.keys()):
        key = request.cookies.get("key")
        if (key == "6sr4h5g135w4ysr9y8q"):
            return static_file(path, root='./')
    else:
        return "error"


# reloader设置为True可以在更新代码时自动重载
# run(host='192.168.3.9', port=8080, reloader=False)
run(host='localhost', port=8080, reloader=False)
