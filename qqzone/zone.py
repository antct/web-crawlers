import sys
import json
import os
import time
import re
import requests
import base


def init():
    base.config = base.read_config()
    if base.config['auto']:
        base.cookie = base.get_cookie_from_auto()
        with open('./config.json') as f:
            con = eval(f.read())
            con['cookie'] = base.cookie
            con['auto'] = False
        with open('./config.json', 'w') as f:
            f.write(str(con))
    else:
        base.cookie = base.get_cookie_from_file()
    base.header['Cookie'] = base.cookie
    base.g_tk = base.get_g_tk()
    base.friends_url = base.get_friends_url()
    base.session = requests.Session()


def __get_friends_list():
    if base.check_path(r"./friends/numbers.txt"):
        return
    print("[%s] <get friends list> start" % (time.ctime(time.time())))
    base.check_path(r"./friends/", new=True)
    position = 0
    while True:
        url = base.friends_url + '&offset=' + str(position)
        base.header['Referer'] = 'http://qzs.qq.com/qzone/v8/pages/setting/visit_v8.html'
        print("[%s] <get friends list> position: %d" % (time.ctime(time.time()), position))
        res = requests.get(url, headers=base.header)
        html = res.text

        # cookie invalid
        if "请先登录" in html:
            print("[%s] <get friends list> some error occur" % (time.ctime(time.time())))
            break

        # html[10: -2] may cause a error
        try:
            html = html[10: -2]
            html_dict = dict(eval(html))
            html_data = html_dict["data"]
            html_list = html_dict["data"]["uinlist"]
        except Exception as e:
            print("[%s] <get friends list> some error occur" % (time.ctime(time.time())))
            print(e)

        if not len(html_list):
            print("[%s] <get friends list> ok" % (time.ctime(time.time())))
            break

        # write initial data crawled from qqzone with format 'json'
        with open('friends/position' + str(position) + '.json', 'w', encoding='utf-8') as f:
            f.write(str(html_data))

        position += 50
        time.sleep(1)

    print("[%s] <process friends> start" % (time.ctime(time.time())))
    friends = [i for i in os.listdir('friends') if i.endswith("json")]
    numbers = []
    for item in friends:
        with open('friends/' + item, encoding='utf-8') as f:
            con = eval(f.read())["uinlist"]
            for i in con:
                numbers.append(i)
    else:
        with open('friends/numbers.txt', 'w', encoding='utf-8') as f:
            print("[%s] <process friends> ok, %d in total" % (time.ctime(time.time()), len(numbers)))
            f.write(str(numbers))


def __get_each_friend_info(num):
    base.header['Referer'] = 'http://user.qzone.qq.com/' + num
    if base.check_path('./results/infos/' + num):
        return
    base.check_path('results/infos/' + num, new=True)
    url_base = base.get_moods_url(num)
    position = 0
    while True:
        print("[%s] <get infos> qq: %s position: %d" % (time.ctime(time.time()), num, position))
        url = url_base + "&pos=%d" % position
        res = base.session.get(url, headers=base.header)
        con = res.text
        con = con[10: -2]
        con_dict = json.loads(con)
        if con_dict["msglist"] is None or con_dict['usrinfo']["msgnum"] == 0:
            break
        if con_dict["subcode"] == -4001:
            sys.exit()

        with open('results/infos/' + num + '/' + str(position) + '.txt', 'w', encoding='utf-8') as f:
            f.write(str(con_dict))

        position += 20
        time.sleep(1)


def __get_all_friends_infos():
    print("[%s] <get infos> start" % (time.ctime(time.time())))
    base.check_path(r'./results/', new=True)
    base.check_path(r'./results/infos/', new=True)
    try:
        with open('friends/numbers.txt', encoding='utf-8') as f:
            numbers_list = eval(f.read())
    except Exception as e:
        print("[%s] <get infos> make sure numbers.txt exists" % (time.ctime(time.time())))
        print(e)

    while numbers_list:
        save = numbers_list[:]
        item = numbers_list.pop()
        qq = item['data']
        print("[%s] <get infos> qq: %s" % (time.ctime(time.time()), qq))
        try:
            __get_each_friend_info(qq)
        # restore the file
        except Exception as e:
            with open('friends/numbers.txt', 'w', encoding='utf-8') as f:
                f.write(str(save))
            print(e)
    else:
        print("[%s] <get infos> ok" % (time.ctime(time.time())))


def __get_given_friends_infos(given):
    print("[%s] <get infos> start" % (time.ctime(time.time())))
    base.check_path(r'./results/', new=True)
    base.check_path(r'./results/infos/', new=True)
    try:
        with open('friends/numbers.txt', encoding='utf-8') as f:
            numbers_list = eval(f.read())
    except Exception as e:
        print("[%s] <get infos> make sure numbers.txt exists" % (time.ctime(time.time())))
        print(e)
    numbers = [i['data'] for i in numbers_list]
    for qq in given:
        if qq in numbers:
            print("[%s] <get infos> qq: %s" % (time.ctime(time.time()), qq))
            try:
                __get_each_friend_info(qq)
            except Exception as e:
                continue
        else:
            continue
    else:
        print("[%s] <get infos> ok" % (time.ctime(time.time())))


def __segment_shuoshuo(num):
    print("[%s] <shuoshuo segment> qq: %s start" % (time.ctime(time.time()), num))
    try:
        with open('./results/shuoshuo/%s.txt' % num, encoding='utf-8') as f:
            content = eval(f.read())
    except Exception as e:
        print("[%s] <shuoshuo segment> make sure %s.txt exists" % (num, time.ctime(time.time())))
        print(e)
    base.check_path(r"./results/", new=True)
    base.check_path(r"./results/shuoshuo/", new=True)
    with open('./results/shuoshuo/%s-seg.txt' % num, 'w', encoding='utf-8') as wf:
        for con in content:
            # replace #
            con, number = re.subn('[#]', "", con)
            # replace [emoji]
            con, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", con)
            wf.write(con)
        print("[%s] <shuoshuo segment> qq: %s ok" % (time.ctime(time.time()), num))


def get_shuoshuo(given):
    __get_friends_list()
    __get_given_friends_infos(given)
    base.check_path(r"./results/", new=True)
    base.check_path(r"./results/shuoshuo/", new=True)
    for num in given:
        print("[%s] <get shuoshuo> qq: %s start" % (time.ctime(time.time()), num))
        files = [i for i in os.listdir('results/infos/%s' % num) if i.endswith(".txt")]
        con = []
        for item in files:
            with open('results/infos/%s/' % num + item, encoding='utf-8') as f:
                msglist = eval(f.read())['msglist']
                for i in msglist:
                    if i['conlist'] is None:
                        continue
                    else:
                        for j in i['conlist']:
                            if 'con' in j.keys():
                                con.append(j['con'])
        else:
            with open('results/shuoshuo/%s.txt' % num, 'w', encoding='utf-8') as f:
                print("[%s] <get shuoshuo> qq: %s ok, %d in total" % (time.ctime(time.time()), num, len(con)))
                f.write(str(con))
        __segment_shuoshuo(num)


def __get_url_photo(url, name, num):
    from PIL import Image
    from io import BytesIO
    base.check_path('./results/photos/%s' % num, new=True)
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        image.save('results/photos/%s/%d.jpg' % (num, name))
    except Exception as e:
        print("[%s] <get photos> qq: %s some error occur" % (time.ctime(time.time()), num))


def __get_urls(num):
    if base.check_path('./results/urls/%s.txt' % num):
        return
    base.check_path(r'./results/', new=True)
    base.check_path(r'./results/urls/', new=True)
    print("[%s] <get urls> qq: %s start" % (time.ctime(time.time()), num))
    files = [i for i in os.listdir('results/infos/%s' % num) if i.endswith(".txt")]
    con = []
    for item in files:
        with open('results/infos/%s/' % num + item, encoding='utf-8') as f:
            msglist = eval(f.read())['msglist']
            for i in msglist:
                if 'pic' not in i.keys() or i['pic'] is None:
                    continue
                else:
                    for j in i['pic']:
                        if 'url2' in j.keys():
                            con.append(j['url2'])
    else:
        with open('results/urls/%s.txt' % num, 'w', encoding='utf-8') as f:
            print("[%s] <get urls> qq: %s ok, %d in total" % (time.ctime(time.time()), num, len(con)))
            f.write(str(con))


def get_photos(given):
    base.check_path(r'./results/', new=True)
    base.check_path(r'./results/photos/', new=True)
    for num in given:
        try:
            print("[%s] <get photos> qq: %s start" % (time.ctime(time.time()), num))
            __get_urls(num)
            with open('./results/urls/%s.txt' % num, encoding='utf-8') as f:
                con = eval(f.read())
                count = 0
                for i in con:
                    __get_url_photo(i, count, num)
                    count += 1
                    print("[%s] <get photos> qq: %s pulling %dth photo" % (time.ctime(time.time()), num, count))
                print("[%s] <get photos> qq: %s ok" % (time.ctime(time.time()), num))
        except Exception as e:
            print("[%s] <get photos> make sure %s.txt exists" % (time.ctime(time.time()), num))
            print(e)
