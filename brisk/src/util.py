import abc
import logging
import os
import random
import threading
from configparser import ConfigParser

import bs4
import redis
import requests
from requests.models import Response

from src.constant import ua

class Logger():
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(Logger, "_instance"):
            with Logger._instance_lock:
                if not hasattr(Logger, "_instance"):
                    Logger._instance = object.__new__(cls)
        return Logger._instance

    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(threadName)s: %(message)s')
        logging.root.setLevel(level=logging.INFO)
        self.logger = logging.getLogger()


class Config():
    _instance_lock = threading.Lock()
    _config_parser = ConfigParser()

    def __new__(cls, *args, **kwargs):
        if not hasattr(Config, "_instance"):
            with Config._instance_lock:
                if not hasattr(Config, "_instance"):
                    Config._instance = object.__new__(cls)
        return Config._instance

    def __init__(self):
        self.__path = r'./config.ini'
        self.config = Config._config_parser
        self.config.read(self.__path, encoding='utf-8')


class DB():
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(DB, "_instance"):
            with DB._instance_lock:
                if not hasattr(DB, "_instance"):
                    DB._instance = object.__new__(cls)
        return DB._instance

    def __init__(self):
        super(DB, self).__init__()
        # TODO
        self.default_db = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.proxy_db = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
        self.db = self.default_db


class Request():
    def __init__(self):
        self.__ua = random.choice(ua)
        self.__headers = {
            'User-Agent': '{}'.format(self.__ua),
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        self.__cookies = None
        self.__session = requests.Session()

    def make(self, headers=None, cookies=None):
        self.headers = headers
        self.cookies = cookies

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, value):
        self.__headers = {
            'User-Agent': '{}'.format(self.__ua),
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        } if not value else value

    @property
    def session(self):
        return self.__session

    @abc.abstractmethod
    def get_token(self):
        pass

    @abc.abstractmethod
    def set_token(self, **kwargs):
        self.__headers.update(**kwargs)

    @abc.abstractmethod
    def clear_token(self):
        pass

    @abc.abstractmethod
    def refresh_token(self):
        pass

    @property
    def cookies(self):
        return self.__cookies

    @cookies.setter
    def cookies(self, value):
        self.__cookies = value

    def get(self, url, params=None, **kwargs):
        return requests.get(url=url, params=params, headers=self.headers, cookies=self.cookies, **kwargs)

    def post(self, url, data, **kwargs):
        return requests.post(url=url, data=data, headers=self.headers, cookies=self.cookies, **kwargs)

    def res2soup(self, response: Response):
        return bs4.BeautifulSoup(response.content, 'lxml')

    def res2json(self, response: Response):
        return response.json()

    def get_soup(self, url, params=None, **kwargs):
        return self.res2soup(self.get(url=url, params=params, **kwargs))

    def get_json(self, url, params=None, **kwargs):
        return self.res2json(self.get(url=url, params=params, **kwargs))


if __name__ == '__main__':
    obj1 = Request()
    obj2 = Request()
    print(id(obj1), id(obj2))
