import sys
import copy
import time
import requests
from urllib import parse
import re
import json
import logging
import bs4

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
logger = logging.getLogger()


class linkedin():
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.csrfToken = None
        self.cookie = None
        self.session = None

    def login(self):
        logger.info('login, get cookies and token')
        self.session = requests.Session()
        r = self.session.get('https://www.linkedin.com/uas/login')
        soup = bs4.BeautifulSoup(r.content, 'lxml')
        loginCsrfParam = soup.find(id='loginCsrfParam-login')['value']
        self.csrfToken = soup.find(id='csrfToken-login')['value']
        sourceAlias = soup.find(id='sourceAlias-login')['value']
        isJsEnabled = soup.find('input', {'name': 'isJsEnabled'})['value']
        source_app = soup.find('input', {'name': 'source_app'})['value']
        tryCount = soup.find('input', {'id': 'tryCount'})['value']
        clickedSuggestion = soup.find(
            'input', {'id': 'clickedSuggestion'})['value']
        signin = soup.find('input', {'name': 'signin'})['value']
        session_redirect = soup.find(
            'input', {'name': 'session_redirect'})['value']
        trk = soup.find('input', {'name': 'trk'})['value']
        fromEmail = soup.find('input', {'name': 'fromEmail'})['value']

        payload = {
            'isJsEnabled': isJsEnabled,
            'source_app': source_app,
            'tryCount': tryCount,
            'clickedSuggestion': clickedSuggestion,
            'session_key': self.username,
            'session_password': self.password,
            'signin': signin,
            'session_redirect': session_redirect,
            'trk': trk,
            'loginCsrfParam': loginCsrfParam,
            'fromEmail': fromEmail,
            'csrfToken': self.csrfToken,
            'sourceAlias': sourceAlias
        }
        r = self.session.post(
            'https://www.linkedin.com/uas/login-submit', data=payload)
        self.cookie = self.session.cookies.get_dict()

    def __crawl(self, url):
        logger.info('try to crawl %s' % url)
        try:
            if len(url) > 0:
                failure = 0
                while failure < 10:
                    try:
                        r = self.session.get(url, timeout=10)
                    except Exception:
                        failure += 1
                        logger.info('fail to crawl, try again')
                        continue
                    if r.status_code == 200:
                        logger.info('crawl ok')
                        return r.content
                    else:
                        logger.info('%s %s' % (r.status_code, url))
                        failure += 2
                if failure >= 10:
                    logger.info('failed: %s' % url)
        except Exception:
            pass

    def __find_my_tag(self, text, tag):
        try:
            return tag, list(set(re.findall("'%s': '(.*?)'" % tag, text)))
        except Exception:
            return None

    def __get_info(self, username):
        url = 'https://www.linkedin.com/in/%s/' % username
        content = self.__crawl(url)
        soup = bs4.BeautifulSoup(content, 'lxml')
        code = soup.findAll('code')
        body_num = None
        str_info = None
        for i in code:
            try:
                text = json.loads(i.text)
                if 'request' in text.keys():
                    if 'profileView' in text['request']:
                        body_num = text['body']
            except Exception:
                continue
        try:
            info = soup.findAll('code', id=body_num)[0]
            info = json.loads(info.text)
            include = info['included']
            str_info = str(include)
        except Exception:
            logger.info('error')
            return

        # print(self.__find_my_tag(str_info, 'firstName'))
        # print(self.__find_my_tag(str_info, 'lastName'))
        # print(self.__find_my_tag(str_info, 'headline'))
        # print(self.__find_my_tag(str_info, 'occupation'))
        # print(self.__find_my_tag(str_info, 'summary'))

        # print(_find_my_tag(str_info, 'connectionsCount'))

        # educations = re.findall("(\{[^\{]*?profile\.Education'[^\}]*?\})", str_info)
        # for education in educations:
        #     item = dict(eval(education))
        #     schoolName = item['schoolName']
        #     degreeName = item['degreeName']
        #     description = item['description']
        #     fieldOfStudy = item['fieldOfStudy']
        #     timePeriod = item['timePeriod']
        #     print(schoolName, degreeName, fieldOfStudy, description)

        positions = re.findall(
            "(\{[^\{]*?profile\.Position'[^\}]*?\})", str_info)
        for position in positions:
            item = dict(eval(position))
            companyName = item['companyName'] if 'companyName' in item.keys(
            ) else None
            title = item['title'] if 'title' in item.keys() else None
            locationName = item['locationName'] if 'locationName' in item.keys(
            ) else None
            timePeriod = item['timePeriod'] if 'timePeriod' in item.keys(
            ) else None
            startDate = endDate = None
            if timePeriod:
                # urn:li:fs_position:(ACoAAAWWIwQB4YZOJM-VYe2miSk3_jNzFqZK8J4,352736941),timePeriod
                time = timePeriod.replace('(', '\(').replace(')', '\)')
                # print(str(soup))
                date = dict(json.loads(re.findall(
                    '(\{[^\{]*?"\$id":"%s,startDate"[^\}]*?\})' % time, str(soup))[0]))
                startYear = date['year'] if 'year' in date.keys() else None
                startMonth = date['month'] if 'month' in date.keys() else None
                startDate = startYear, startMonth
                try:
                    date = dict(
                        json.loads(re.findall('(\{[^\{]*?"\$id":"%s,endDate"[^\}]*?\})' % time, str(soup))[0]))
                    endYear = date['year'] if 'year' in date.keys() else None
                    endMonth = date['month'] if 'month' in date.keys() else None
                    endDate = endYear, endMonth
                except Exception:
                    endDate = 'up to date'
            print()
            print(title, companyName, locationName, startDate, endDate)

    def search(self, keyword):
        # https://www.linkedin.com/voyager/api/search/blended?
        # keywords=%E8%8C%83%E6%80%A1%E5%A9%B7&origin=TYPEAHEAD_ESCAPE_HATCH&
        # count=10&queryContext=List(spellCorrectionEnabled-%3Etrue)&q=all&
        # filters=List()&start=0
        session = self.session
        payload = {
            'keywords': keyword,
            'origin': 'TYPEAHEAD_ESCAPE_HATCH',
            'count': 10,
            'queryContext': 'List(spellCorrectionEnabled->true)',
            'q': 'all',
            'filters': 'List()',
            'start': 0,
        }
        headers = {
            'csrf-token': self.csrfToken
        }
        url = r'https://www.linkedin.com/voyager/api/search/blended?'
        r = session.get(url, headers=headers, params=payload)
        try:
            persons = dict(eval(r.text.replace('false', 'False').replace('true', 'True')))[
                'elements']
            persons = persons[0]
            persons = persons['elements']
            persons = persons[0]
            publicIdentifier = persons['publicIdentifier']
            username = parse.quote(publicIdentifier)
            logger.info('username: %s' % username)
            self.__get_info(username=username)
        except Exception:
            logger.info('error')
            return


obj = linkedin()
obj.login()
obj.search('Ray Dalio')
# obj.print_user_info(username='stone-wang-31847b27')


# print(code)
