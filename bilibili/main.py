import requests
import json
import re
import datetime
import logging
import time
import argparse

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(threadName)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
logger = logging.getLogger()

parser = argparse.ArgumentParser()
parser.add_argument('-i', help='url to crawl')
parser.add_argument('-o', help='target file to save')     
args = parser.parse_args()

class bilibili():
    def __init__(self):
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'Connection': 'keep-alive'
        }
        self._session = requests.Session()

        import http.cookiejar

        with open('./cookie.json', 'r') as f:
            self._cookies = json.loads(f.read())

        self._cookiejar = http.cookiejar.CookieJar()
        for cookie in self._cookies:
            self._cookiejar.set_cookie(
                http.cookiejar.Cookie(
                    version=0, name=cookie['name'], value=cookie['value'], port=None, port_specified=False,
                    domain=cookie['domain'], domain_specified=False, domain_initial_dot=False, path=cookie['path'],
                    path_specified=True, secure=cookie['secure'], expires=None, discard=True, comment=None,
                    comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
            )
        self._session.cookies = self._cookiejar
        self._month = '2019-04'


    # get the basic info of input url
    def _get_url_info(self, url):
        logger.info('fetch basic info')
        av = url.rpartition('av')[2]
        logger.info('av: {}'.format(av))
        res = requests.get(url, headers=self._headers)
        oid = re.findall('"cid":(.*?),"dimension"', res.text)[0]
        logger.info('oid: {}'.format(oid))
        upload_date = re.findall('<meta data-vue-meta="true" itemprop="uploadDate" content="(.*?)">', res.text)[0]
        upload_month = upload_date[:7]
        logger.info('upload month: {}'.format(upload_month))
        return oid, upload_month

        
    def _get_dm_index(self, oid, upload_month):
        months = []
        upload_t = upload_month
        logger.info('get the months to crawl')
        while upload_t <= self._month:
            months.append(upload_t)
            year_int = int(upload_t[:4])
            month_int = int(upload_t[5:])
            if month_int != 12:
                month_int += 1
            else:
                year_int += 1
                month_int = 1
            upload_t = '{:4d}-{:02d}'.format(year_int, month_int)

        logger.info('months from {} to {}, {} in total'.format(months[0], months[-1], len(months)))
        logger.info('get the dates to crawl')

        dates = []
        for month in months:
            url = 'https://api.bilibili.com/x/v2/dm/history/index?type=1&oid={}&month={}'.format(oid, month)
            res = self._session.get(url=url, headers=self._headers).json()
            for date in res['data']:
                dates.append(date)

        logger.info('dates from {} to {}, {} in total'.format(dates[0], dates[-1], len(dates)))
        return dates

    def _get_dm(self, url, target):

        oid, upload_month = self._get_url_info(url)

        dates = self._get_dm_index(oid, upload_month)

        logger.info('get danmu')

        dm_list = []
        for date in dates:
            url = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid={}&date={}'.format(oid, date)
            res = self._session.get(url=url, headers=self._headers)
            res.encoding = 'utf-8'
            dms = []
            dms = re.findall('<d.*?</d>', res.text)
            #print(danmuku_time)
            for dm in dms:
                # 记录弹幕时间(浮点数)
                dm_show = re.findall('<d p="(.*?),', dm)[0]
                dm_unix = re.findall('<d p=".*?,.*?,.*?,.*?,(.*?),', dm)[0]
                dm_text = re.findall('<d.*?>(.*?)</d>', dm)[0]
                dm_time = datetime.datetime.fromtimestamp(float(dm_unix))
                dm_list.append((str(dm_time), dm_show, dm_text))
            logger.info('{} danmu in {}, {} in total'.format(len(dms), date, len(dm_list)))
            logger.info('sleep 1s')
            time.sleep(1)
        dm_set = list(set(dm_list))
        dm_set = sorted(dm_set, key=lambda d:d[1], reverse=False)
        dm_set = sorted(dm_set, key=lambda d:d[0], reverse=False)
        
        import csv
        count = 0
        logger.info('write to {}'.format(target))
        with open(target, 'w+', newline='', encoding='utf-8-sig') as wf:
            csv_wf = csv.writer(wf, dialect='excel')
            csv_wf.writerow(['序号', '发送时间', '出现时间(秒)', '内容'])
            for i in dm_set:
                count += 1
                csv_wf.writerow([count, i[0], i[1], i[2]])
        



if __name__ == "__main__":
    obj = bilibili()
    obj._get_dm(args.i, args.o)
