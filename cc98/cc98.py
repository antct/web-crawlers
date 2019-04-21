import urllib.request
import urllib.parse
import json
import re
import redis
import os
import time


class cc98_authorization():
    def __init__(self, fname='./config.json'):
        self.url = r'https://openid.cc98.org/connect/token'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
            'Connection': 'keep-alive',
        }
        # read config from ./config.json
        self.config = {}
        with open(fname, 'r') as f:
            self.config = json.loads(f.read())
        self.redis = redis.Redis(
            host='127.0.0.1', port=6379, decode_responses=True)

    def __print(self, type, text, segment=False):
        print("============================================================") if segment == True else print(
            "", end="")
        print('{} - {}: {}'.format(time.strftime("%Y/%m/%d %I:%M:%S"), type, text))
        print("============================================================") if segment == True else print(
            "", end="")

    # post data to the given url
    def __post(self, url, data):
        formdata = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(
            url, headers=self.headers, data=formdata)
        try:
            response = json.loads(urllib.request.urlopen(
                request).read().decode('utf-8'))
            return response
        except:
            self.__print('error', 'network error')

    # save and update token in redis
    def __set_token(self):
        self.redis.set('token', self.token, ex=self.expire_time)
        self.redis.set('token_type', self.token_type)
        # here, refresh_token: 30 days, access_token: 1 hour
        self.redis.set('refresh_token', self.refresh_token,
                       ex=24 * 30 * self.expire_time)

    def __fresh_token(self):
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'refresh_token': self.redis.get('refresh_token'),
        }
        response = self.__post(self.url, data)
        self.token_type, self.token = response['token_type'], response['access_token']
        self.expire_time, self.refresh_token = response['expires_in'], response['refresh_token']
        self.__set_token()

    def clear_token(self):
        self.redis.delete('token')
        self.redis.delete('refresh_token')

    def __refresh_header(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
            'Connection': 'keep-alive',
            'authorization': '%s %s' % (self.redis.get('token_type'), self.redis.get('token'))
        }

    def get_token(self):
        if self.redis.get('token') != None:
            self.__print("info", "token already exists, use old valid token")
            self.__refresh_header()
            return
        if self.redis.get('refresh_token') != None:
            self.__print("info", "token expired, try to refresh token")
            self.__fresh_token()
            self.__print("info", "token refreshed")
            self.__refresh_header()
            return
        self.__print("info", "try to get token with username & password")
        data = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'grant_type': 'password',
            'username': self.config['username'],
            'password': self.config['password'],
        }
        response = self.__post(self.url, data)
        self.token_type, self.token = response['token_type'], response['access_token']
        self.expire_time, self.refresh_token = response['expires_in'], response['refresh_token']
        self.__set_token()
        self.__refresh_header()
        self.__print("info", "token acquired")


class cc98_api(cc98_authorization):
    def __init__(self):
        cc98_authorization.__init__(self)
        self.boards = {}
        self.get_boards()

    def __get(self, url):
        request = urllib.request.Request(url, headers=self.headers)
        try:
            response = urllib.request.urlopen(request).read().decode('utf-8')
            return json.loads(response)
        except:
            pass

    def __get_params(self, url, params):
        url = url + '?' + \
            str(urllib.parse.urlencode(params).encode('utf-8'), encoding='utf-8')
        return self.__get(url)

    def get_boards(self):
        # 这个API是不需要token验证的
        zones = self.__get(r'https://api.cc98.org/board/all')
        for zone in zones:
            for item in zone['boards']:
                self.boards[item['name']] = item['id']

    # 首页信息
    def get_index(self):
        return self.__get(r'https://api.cc98.org/config/index')

    # 首页公告
    def get_index_announcement(self):
        return self.__get(r'https://api.cc98.org/config/index')['announcement']

    # 首页热门主题
    def get_index_hot_topic(self):
        return self.__get(r'https://api.cc98.org/config/index')['hotTopic']

    # 首页推荐阅读
    def get_index_recommendation_reading(self):
        return self.__get(r'https://api.cc98.org/config/index')['recommendationReading']

    # 首页校园活动
    def get_index_school_event(self):
        return self.__get(r'https://api.cc98.org/config/index')['schoolEvent']

    # 首页学术信息
    def get_index_academics(self):
        return self.__get(r'https://api.cc98.org/config/index')['academics']

    # 首页校园新闻
    def get_index_school_news(self):
        return self.__get(r'https://api.cc98.org/config/index')['schoolNews']

    # 未阅读信息
    def get_unread_count(self):
        return self.__get(r'https://api.cc98.org/me/unread-count')

    # 历史热门
    def get_hot_topic_history(self):
        return self.__get(r'https://api.cc98.org/topic/hot-history')

    # 本周热门
    def get_hot_topic_weekly(self):
        return self.__get(r'https://api.cc98.org/topic/hot-weekly')

    # 本月热门
    def get_hot_topic_monthly(self):
        return self.__get(r'https://api.cc98.org/topic/hot-monthly')

    # 今日热门
    def get_hot_topic_daily(self):
        return self.__get(r'https://api.cc98.org/topic/hot')

    # 个人信息
    def get_me_info(self):
        return self.__get(r'https://api.cc98.org/me')

    # 个人最近发帖
    def get_me_recent_topic(self):
        params = {
            'from': 0,
            'size': 11,
        }
        return self.__get_params(r'https://api.cc98.org/me/recent-topic', params=params)

    # 回复我的
    def get_notification_reply(self):
        params = {
            'from': 0,
            'size': 10
        }
        return self.__get_params(r'https://api.cc98.org/notification/reply', params=params)

    # @我的
    def get_notification_at(self):
        params = {
            'from': 0,
            'size': 10
        }
        return self.__get_params(r'https://api.cc98.org/notification/at', params=params)

    # 系统通知
    def get_notification_system(self):
        params = {
            'from': 0,
            'size': 10
        }
        return self.__get_params(r'https://api.cc98.org/notification/system', params=params)

    # 最近聊天用户
    def get_user_recent_contact(self):
        params = {
            'from': 0,
            'size': 7
        }
        return self.__get_params(r'https://api.cc98.org/message/recent-contact-users', params=params)

    # 与用户沟通信息
    def get_message_with_user(self, user_id):
        params = {
            'from': 0,
            'size': 10
        }
        return self.__get_params(r'https://api.cc98.org/message/user/%d' % user_id, params=params)

    # 某版块文章
    def get_board_posts(self, board_name, page_start=0, page_end=1):
        if board_name not in self.boards.keys():
            return
        data = {
            'from': 0,
            'size': 20,
        }
        posts = []
        for page in range(page_start, page_end):
            data['from'] = data['size'] * page
            items = self.__get_params(url=r'https://api.cc98.org/board/%d/topic' % (self.boards[board_name]),
                                      params=data)
            for item in items:
                posts.append(item)
        return posts

    # 文章内容
    def get_post_content(self, post_id, pages=1, comment=True):
        params = {
            'from': 0,
            'size': 10,
        }
        contents = []
        for page in range(pages):
            params['from'] = params['size'] * page
            items = self.__get_params(
                url=r'https://api.cc98.org/Topic/%d/post' % (post_id), params=params)
            for item in items:
                contents.append(item)
        contents = contents if comment is True else contents[0:1]
        return contents

    # 最新文章
    def get_new_posts(self, pages=1):
        params = {
            'from': 0,
            'size': 10,
        }
        posts = []
        for page in range(pages):
            params['from'] = params['size'] * page
            items = self.__get_params(
                url=r'https://api.cc98.org/topic/new', params=params)
            for item in items:
                posts.append(item)
        return posts

    # 所有版块搜索

    def search_post_all_boards(self, keyword, pages=1):
        params = {
            'from': 0,
            'size': 20,
            'keyword': keyword,
        }
        results = []
        for page in range(pages):
            params['from'] = params['size'] * page
            items = self.__get_params(
                r'https://api.cc98.org/topic/search', params=params)
            for item in items:
                results.append(item)
        return results

    # 某个版块搜索
    def search_post_one_board(self, board_name, keyword, pages=1):
        if board_name not in self.boards.keys():
            return
        params = {
            'from': 0,
            'size': 20,
            'keyword': keyword,
        }
        results = []
        for page in range(pages):
            params['from'] = params['size'] * page
            items = self.__get_params(r'https://api.cc98.org/topic/search/board/%d' % self.boards[board_name],
                                      params=params)
            for item in items:
                results.append(item)
        return results

    # 依靠用户名搜索
    def search_user_by_username(self, username):
        return self.__get(r'https://api.cc98.org/user/name/' + str(urllib.request.quote(username)))

    # 依靠id搜索
    def search_user_by_id(self, user_id):
        return self.__get(r'https://api.cc98.org/user/' + str(user_id))

    # 得到用户最近发帖
    def get_user_recent_topic(self, username):
        user = self.search_user_by_username(username)
        if user == None:
            return
        params = {
            'userid': user['id'],
            'from': 0,
            'size': 11,
        }
        return self.__get_params(r'https://api.cc98.org/user/%d/recent-topic' % user['id'], params=params)


from multiprocessing import Process, Queue


class cc98_crawler(cc98_api, Process):
    def __init__(self, **kwargs):
        cc98_api.__init__(self)
        Process.__init__(self)
        self.kwargs = kwargs
        self.get_token()

    def run(self):
        pass