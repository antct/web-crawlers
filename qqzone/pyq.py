import base
import re
import time
import os
import requests


def __segment_pyq():
    print("[%s] <pyq segment> start" % (time.ctime(time.time())))
    base.check_path('./results/', new=True)
    base.check_path('./results/words/', new=True)
    with open('./exported_sns.json', encoding='utf-8') as f:
        raw = f.read().replace("false", "False").replace("true", "True")
        raw_content = eval(raw)
    content = []
    for i in raw_content:
        content.append(i["content"])
    with open('./results/words/pyq-seg.txt', 'w', encoding='utf-8') as wf:
        for con in content:
            # replace #
            con, number = re.subn('[#]', "", con)
            # replace [emoji]
            con, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", con)
            wf.write(con)
        print("[%s] <pyq segment> ok" % (time.ctime(time.time())))


def get_words():
    if not base.check_path("./exported_sns.json"):
        print("[%s] <get pyq> make sure exported_sns.json exists" % (time.ctime(time.time())))
        return
    __segment_pyq()


def __get_url_photo(url, name):
    from PIL import Image
    from io import BytesIO
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        image.save('results/pyq-photos/%d.jpg' % (name))
    except Exception as e:
        print("[%s] <get photos> some error occur" % (time.ctime(time.time())))


def __get_urls():
    if base.check_path('./results/pyq-urls/urls.txt'):
        return
    base.check_path(r'./results/', new=True)
    base.check_path(r'./results/pyq-urls/', new=True)
    print("[%s] <get urls> start" % (time.ctime(time.time())))
    with open('./exported_sns.json', encoding='utf-8') as f:
        raw = f.read().replace("false", "False").replace("true", "True")
        raw_content = eval(raw)
    contents = []
    for i in raw_content:
        contents.append(i["rawXML"])
    urls = []
    for con in contents:
        # replace #
        li = re.findall(r'<url\ type\ =\ \ "1"\ ><!\[CDATA\[(.*?)\]\]><\\/url>', con)
        for i in li:
            urls.append(i.replace("\/", "/"))
    with open('./results/pyq-urls/urls.txt', "w") as f:
        f.write(str(urls))
    print("[%s] <get urls> ok" % (time.ctime(time.time())))


def get_photos():
    print("[%s] <get photos> start" % (time.ctime(time.time())))
    base.check_path('./results/', new=True)
    base.check_path('./results/pyq-photos/', new=True)
    __get_urls()
    with open('./results/pyq-urls/urls.txt') as f:
        li = eval(f.read())
    for i in range(len(li)):
        print("[%s] <get photos> pulling %dth photo" % (time.ctime(time.time()), i + 1))
        __get_url_photo(li[i], i + 1)
    print("[%s] <get photos> ok" % (time.ctime(time.time())))
