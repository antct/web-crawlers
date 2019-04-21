import hashlib
import time
import random
import re
import string
from urllib.parse import quote
import requests
import base

def __curl_md5(src):
    # md5
    m = hashlib.md5()
    m.update(src.encode('utf-8'))
    return m.hexdigest()


def __get_params(plus_item):
    # request timestamp
    t = time.time()
    time_stamp = str(int(t))

    # request a random string
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))

    # config.json
    app_id = base.config['app_id']
    app_key = base.config['app_key']

    params = {'app_id': app_id,
              'text': plus_item,
              'time_stamp': time_stamp,
              'nonce_str': nonce_str,
              'sign': ''
              }
    sign_before = ''
    for key in sorted(params):
        if params[key] != '':
            # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8，而不是小写%e8。quote默认的大写。
            sign_before += key + '=' + quote(params[key]) + '&'
            # 将应用密钥以app_key为键名，组成URL键值拼接到字符串sign_before末尾
    sign_before += 'app_key=' + app_key

    # 对字符串S进行MD5运算，将得到的MD5值所有字符转换成大写，得到接口请求签名
    sign = __curl_md5(sign_before)
    sign = sign.upper()
    params['sign'] = sign

    return params


def get_text_feel(num):
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textpolar"
    text_url = './results/shuoshuo/%s.txt' % num
    print("[%s] <get text feel> start" % (time.ctime(time.time())))
    try:
        with open(text_url, encoding='utf-8') as f:
            all_chaps = eval(f.read())
    except Exception as e:
        print("[%s] <get text feel> make sure %s.txt exists" % (time.ctime(time.time()), num))
        print(e)
    valid_count = 0
    for plus_item in all_chaps:
        plus_item, number = re.subn('[#]', "", plus_item)
        plus_item, number = re.subn(r'\[(.*?)\](.*?)\[(.*?)\]', "", plus_item)
        payload = __get_params(plus_item)  # 获取请求参数
        r = requests.get(url, params=payload)
        if r.json()['ret'] == 0:
            polar = r.json()['data']['polar']
            print('confidence: %d, polar: %s, text: %s' % (r.json()['data']['confd'],
                  '负面' if polar == -1 else '中性' if polar == 0 else '正面', r.json()['data']['text']))
            valid_count += 1
    print("[%s] <get text feel> ok" % (time.ctime(time.time())))
    print("[%s] <get text feel> %d valid, %d in total" % (time.ctime(time.time()), valid_count, len(all_chaps)))

def __gen_word_cloud(text_url, mask_url):
    import jieba
    from scipy.misc import imread
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
    try:
        with open(text_url, encoding='utf-8') as f:
            all_chaps = [chap for chap in f.readlines()]
    except Exception as e:
        print("[%s] <get word cloud> make sure *-seg.txt exists" % (time.ctime(time.time())))
        print(e)
    dictionary = []
    for i in range(len(all_chaps)):
        words = list(jieba.cut(all_chaps[i]))
        dictionary.append(words)

    # flat
    tmp = []
    for chapter in dictionary:
        for word in chapter:
            tmp.append(word.encode('utf-8'))
    dictionary = tmp

    # filter
    unique_words = list(set(dictionary))

    freq = []
    for word in unique_words:
        freq.append((word.decode('utf-8'), dictionary.count(word)))

    # sort
    freq.sort(key=lambda x: x[1], reverse=True)

    # broke_words
    broke_words = []

    try:
        with open('word/stopwords.txt') as f:
            broke_words = [i.strip() for i in f.readlines()]
    except Exception as e:
        broke_words = STOPWORDS

    # remove broke_words
    freq = [i for i in freq if i[0] not in broke_words]

    # remove monosyllable words
    freq = [i for i in freq if len(i[0]) > 1]

    img_mask = imread(mask_url)
    img_colors = ImageColorGenerator(img_mask)

    wc = WordCloud(background_color="white",  # bg color
                   max_words=2000,  # max words
                   font_path=u'./word/SourceHanSans-Regular.otf',
                   mask=img_mask,  # bg image
                   max_font_size=60,  # max font size
                   random_state=42)

    wc.fit_words(dict(freq))

    plt.imshow(wc)
    plt.axis('off')
    plt.show()


def get_zone_word_cloud(num, mask="Male"):
    print("[%s] <get zone word cloud> start" % (time.ctime(time.time())))
    text_url = './results/shuoshuo/%s-seg.txt' % num
    mask_url = './word/alice_mask.png' if mask == "Female" else './word/boy_mask.png'
    if not base.check_path(text_url):
        print("[%s] <get zone word cloud> make sure %s-seg.txt exists" % (time.ctime(time.time()), num))
        return
    __gen_word_cloud(text_url, mask_url)
    print("[%s] <get zone word cloud> ok" % (time.ctime(time.time())))

def get_pyq_word_cloud(mask="Male"):
    print("[%s] <get pyq word cloud> start" % (time.ctime(time.time())))
    text_url = './results/pyq/pyq-seg.txt'
    mask_url = './word/alice_mask.png' if mask == "Female" else './word/boy_mask.png'
    if not base.check_path(text_url):
        print("[%s] <get pyq word cloud> make sure pyq-seg.txt exists" % (time.ctime(time.time())))
        return
    __gen_word_cloud(text_url, mask_url)
    print("[%s] <get pyq word cloud> ok" % (time.ctime(time.time())))