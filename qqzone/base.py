from urllib import parse
import os
import time

cookie = None
header = {'host': 'h5.qzone.qq.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh,zh-CN;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': None,
            'connection': 'keep-alive'}
g_tk = None
friends_url = None
session = None
config = None

def check_path(path, new=False):
    if os.path.exists(path):
        return True
    else:
        if new == True:
            os.mkdir(path)
            return True
        return False


def read_config():
    con = {}
    try:
        with open('./config.json') as f:
            con = eval(f.read())
    except Exception as e:
        print("[%s] <error> check your json format" % (time.ctime(time.time())))
        print(e)
    return con


def get_cookie_from_file():
    return config['cookie']


def get_cookie_from_auto():
    from selenium import webdriver
    print("[%s] <get cookies> start" % (time.ctime(time.time())))

    # set firefox headless, run in background
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.set_headless()
    driver = webdriver.Firefox(firefox_options=firefox_options)

    url = 'https://qzone.qq.com/'
    driver.get(url)
    # switch frame to login frame, important
    driver.switch_to.frame('login_frame')
    time.sleep(1)
    driver.find_element_by_id('switcher_plogin').click()
    time.sleep(1)
    driver.find_element_by_id('u').send_keys(config['username'])
    driver.find_element_by_id('p').send_keys(config['password'])
    time.sleep(1)
    driver.find_element_by_id('login_button').click()
    time.sleep(1)

    cookie = ""
    for item in driver.get_cookies():
        cookie += item["name"] + "=" + item["value"] + "; "
    driver.quit()

    print("[%s] <get cookies> ok" % (time.ctime(time.time())))
    return cookie


def get_g_tk():
    start = cookie.find('p_skey=')
    end = cookie.find(';', start)
    key = cookie[start + 7: end]
    h = 5381
    for s in key:
        h += (h << 5) + ord(s)
    return h & 2147483647


def get_moods_url(num):
    params = {"cgi_host": "http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6",
              "code_version": 1,
              "format": "jsonp",
              "g_tk": g_tk,
              "hostUin": num,
              "inCharset": "utf-8",
              "need_private_comment": 1,
              "notice": 0,
              "num": 20,
              "outCharset": "utf-8",
              "sort": 0,
              "uin": num}
    host = "https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?"
    return host + parse.urlencode(params)


def get_friends_url():
    qq_start = cookie.find('uin=o')
    qq_end = cookie.find(';', qq_start)
    qq_num = cookie[qq_start + 5: qq_end]
    if qq_num[0] == 0:
        qq_num = qq_num[1:]
    params = {"uin": qq_num,
              "fupdate": 1,
              "action": 1,
              "g_tk": g_tk}
    host = "https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?"
    return host + parse.urlencode(params)

