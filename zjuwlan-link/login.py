# -*- coding: utf-8 -*-
# !/usr/bin/env python
# encoding:UTF-8

import requests
import sys
import re
import sys
import time
import base64
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def login(username, password):
    print('[infos] try to connect the network')
    headers = {'Accept': '*/*',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    s = requests.Session()
    s.headers = headers
    post_data = {'action': 'login', 'username': username, 'password': password, 'ac_id': '3', 'save_me': '1',
                 'ajax': '1'}
    count = 0
    while True:
        try:
            r = s.post('https://net.zju.edu.cn/include/auth_action.php', data=post_data, verify=False)
            r.encoding = 'utf-8'
            pattern = re.compile(r'login_ok')
            match = pattern.match(r.text)
            if match:
                break
            count += 1
            if count == 15:
                print('[error] too many failed attempts, check your account')
                return
            print('[error] connection failed, the %dth attempt' % (count + 1))
            time.sleep(0.5)
        except:
            continue
    print('[infos] connection succeeded')


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    username = ""
    password = ""
    try:
        file = open("./config.json", "r")
    except FileNotFoundError:
        print('[infos] please provide the VPN account password first')
        print("[infos] username:", end=" ")
        s1 = input()
        print("[infos] password:", end=" ")
        s2 = input()
        s = "{'username': '%s', 'password': '%s'}" % (s1, s2)
        s_byte = bytes(s, "utf-8")
        s_encode = base64.encodestring(s_byte)
        s_mm = str(s_encode, "utf-8")
        file = open("./config.json", "w")
        file.write(s_mm)
        file.close()
    finally:
        file = open("./config.json", "r")
        s = str(base64.decodestring(bytes(file.readline(), encoding="utf8")), encoding="utf-8")
        s_dict = dict(eval(s))
        username = s_dict['username']
        password = s_dict['password']
        file.close()

    login(username, password)
    input('[infos] press <enter>')
