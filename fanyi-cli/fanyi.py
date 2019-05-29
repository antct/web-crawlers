# -*- coding: utf-8 -*-
#!/usr/bin/env python
# encoding:UTF-8

import requests
import bs4
import sys


class fanyi():
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        self.sess = requests.Session()
        self.youdao_url = 'http://www.youdao.com/w/'
        self.ciba_url = 'http://www.iciba.com/'

    def __youdao_search(self, keyword):
        r = self.sess.get(self.youdao_url + keyword)
        soup = bs4.BeautifulSoup(r.content, 'lxml')

        wordGroup = soup.find(class_='wordGroup')
        search_js = wordGroup.find_all(class_='search-js')
        search_text = [i.text for i in search_js]

        phrsListTab = soup.find(id='phrsListTab')

        keyword = phrsListTab.find(class_='keyword').text
        phonetic = [i.text for i in phrsListTab.find_all(class_='phonetic')]

        trans_container = phrsListTab.find(class_='trans-container')
        trans_items = [i.text for i in trans_container.find_all('li')]

        print('\033[33m{}'.format(keyword))
        for i in phonetic:
            print('\033[35m{}'.format(i), end=' ')
        print()
        for i in search_text:
            print('\033[36m{}'.format(i), end=' ')
        print()
        for i in trans_items:
            print('\033[31m{}'.format(i))

    def __ciba_search(self, keyword):
        r = self.sess.get(self.ciba_url + keyword)
        soup = bs4.BeautifulSoup(r.content, 'lxml')

        in_base = soup.find(class_='in-base')

        keyword = in_base.find(class_='keyword').text.strip()
        phonetic = [i.text for i in in_base.find(
            class_='base-speak').find_all('span')]
        phonetic = [i for i in phonetic if phonetic.index(i) % 2]

        trans_container = in_base.find(class_='base-list switch_part')
        trans_items = [i.text for i in trans_container.find_all('li')]
        trans_items = [i.replace('\n\n', ' ').replace('\n', '')
                       for i in trans_items]

        print('\033[33m{}'.format(keyword))
        for i in phonetic:
            print('\033[35m{}'.format(i), end=' ')
        print()
        for i in trans_items:
            print('\033[31m{}'.format(i))

    def search(self, keyword):
        print('\033[32m{}'.format('youdao'))
        self.__youdao_search(keyword)
        print()
        print('\033[32m{}'.format('iciba'))
        self.__ciba_search(keyword)
        print('\033[0m', end='')


obj = fanyi()
obj.search(sys.argv[1])
