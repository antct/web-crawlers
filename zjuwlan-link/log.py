# -*- coding: utf-8 -*-
#!/usr/bin/env python
# encoding:UTF-8

import requests
import sys
import re
import time
import base64
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class ZJUWLAN():
    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        self.sess = requests.Session()
        self.sess.headers = self.headers
        self.url = 'https://net.zju.edu.cn/include/auth_action.php'
        self.path = './config.json'
        self.max_times = 20
        self.__init_config()

    def __print(self, text, nl=True):
        if nl:
            print('{} - INFO: {}'.format(time.strftime("%Y/%m/%d %I:%M:%S"), text))
        else:
            print(
                '{} - INFO: {}'.format(time.strftime("%Y/%m/%d %I:%M:%S"), text), end='')

    def __init_config(self):
        try:
            f = open(self.path, "r")
            encrypt_s = f.read()
            f.close()
            origin_s = str(base64.decodestring(
                bytes(encrypt_s, encoding="utf8")), encoding="utf-8")
            s_dict = dict(eval(origin_s))
            self.username = s_dict['username']
            self.password = s_dict['password']
        except FileNotFoundError:
            self.__print('Please provide the VPN account password first.')
            self.__print('Username: ', nl=False)
            origin_username = input()
            self.__print('Password: ', nl=False)
            origin_password = input()
            self.username = origin_username
            self.password = origin_password
            origin_s = bytes("{'username': '%s', 'password': '%s'}" % (
                origin_username, origin_password), 'utf-8')
            encrypt_s = str(base64.encodestring(origin_s), 'utf-8')
            with open(self.path, 'w+') as wf:
                wf.write(encrypt_s)

    def login(self):
        self.__print('Try to connect to ZJUWLAN.')
        data = {
            'action': 'login',
            'username': self.username,
            'password': self.password,
            'ac_id': '3',
            'save_me': '0',
            'ajax': '1'
        }
        pattern1 = re.compile(r'login_ok')
        pattern2 = re.compile(r'E2532')
        pattern3 = re.compile(r'E2531')
        pattern4 = re.compile(r'E2901')
        for i in range(self.max_times):
            try:
                r = self.sess.post(self.url, timeout=1.0,
                                   data=data, verify=False)
                r.encoding = 'utf-8'
                r_text = r.text
                if i == 0 and pattern3.match(r_text):
                    self.__print('Username not exists.')
                    return
                if i == 0 and pattern4.match(r_text):
                    self.__print('Wrong password.')
                    return
                if pattern1.match(r_text):
                    self.__print('Connection established.')
                    return
                if pattern2.match(r_text):
                    self.__print(
                        'The two authentication interval cannot be less than 10 seconds.')
                time.sleep(0.5)
            except:
                self.__print('Make sure the AP is connected to ZJUWLAN.')
                return
        self.__print('Too many failed attempts, check your account.')

    def logout(self):
        self.__print('Try to disconnect from ZJUWLAN.')
        data = {
            'action': 'logout',
            'username': self.username,
            'password': 'adad',
            'ajax': '1'
        }
        pattern1 = re.compile(r'网络已断开')
        pattern2 = re.compile(r'您似乎未曾连接到网络')
        pattern3 = re.compile(r'注销失败')
        for i in range(self.max_times):
            try:
                r = self.sess.post(self.url, timeout=1.0,
                                   data=data, verify=False)
                r.encoding = 'utf-8'
                r_text = r.text
                if i == 0 and pattern2.match(r_text):
                    self.__print('No connections or username not exists.')
                    return
                if i == 0 and pattern3.match(r_text):
                    self.__print('Wrong password.')
                    return
                if pattern1.match(r_text):
                    self.__print('Connection canceled.')
                    return
                time.sleep(0.5)
            except:
                self.__print('Make sure the AP is connected to ZJUWLAN.')
                return
        self.__print('Too many failed attempts, check your account.')


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    obj = ZJUWLAN()
    if sys.argv[1] == "login":
        obj.login()
    elif sys.argv[1] == "logout":
        obj.logout()
