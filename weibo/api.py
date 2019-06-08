import requests
import bs4
import re

class weibo():
    def __init__(self, config='./weibo.config'):
        self._config = None
        with open(config, 'r') as f:
            self._config = eval(f.read())

        self._username = self._config['username']
        self._password = self._config['password']


        self._headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'close',
            'Host': 'passport.weibo.cn',
            'Origin': 'https://passport.weibo.cn',
            'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'
        }
        self._session = requests.Session()


    def login(self):
        data = {
            'entry': 'mweibo',
            'pagerefer': 'https://passport.weibo.cn/signin/welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F&wm=3349&vt=4',
            'savestate': '1',
            'ec': 0
        }

        data['username'] = self._username
        data['password'] = self._password

        res = self._session.post(url='https://passport.weibo.cn/sso/login', data=data, headers=self._headers)
        # print(res.text)

    def get_user_info(self, user_id):
        res = self._session.get(url='https://weibo.cn/{}/info'.format(user_id))
        print(res.text)

    
    def get_fans(self, user_id):
        res = self._session.get(url='https://weibo.cn/{}/fans'.format(user_id))
        
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        page = None

        try:
            pagelist = soup.find(id='pagelist')
            pageinfo = pagelist.text.strip().split()[1]
            page = int(pageinfo[-2])
        except Exception:
            page = 1


        fans = []
        for i in range(1, page + 1):
            res = self._session.get(url='https://weibo.cn/{}/fans?page={}'.format(user_id, i))
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            tables = soup.findAll('table')
            # 1 table <-> 1 fan
            for table in tables:
                trs = table.findAll('tr')
                for tr in trs:
                    tds = tr.findAll('td')
                    href = tds[0].find('a').get('href')
                    # https://weibo.cn/u/2667215760
                    fan_id = href[19:]
                    fans.append(fan_id)

        return fans

    def get_follows(self, user_id):
        res = self._session.get(url='https://weibo.cn/{}/follow'.format(user_id))
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        page = None

        try:
            pagelist = soup.find(id='pagelist')
            pageinfo = pagelist.text.strip().split()[1]
            page = int(pageinfo[-2])
        except Exception:
            page = 1


        follows = []
        for i in range(1, page + 1):
            res = self._session.get(url='https://weibo.cn/{}/follow?page={}'.format(user_id, i))
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            tables = soup.findAll('table')
            # 1 table <-> 1 fan
            for table in tables:
                trs = table.findAll('tr')
                for tr in trs:
                    tds = tr.findAll('td')
                    href = tds[1].findAll('a')[-1].get('href')
                    # https://weibo.cn/im/chat?uid=1929266145&amp;rl=1
                    follow_id = href[href.find('?')+1:href.find('&')]
                    follow_id = follow_id[4:]
                    follows.append(follow_id)

        return follows

    def get_commons(self, user_id):
        follows = self.get_follows(user_id)
        fans = self.get_fans(user_id)
        commons = []
        for person in fans:
            if person in follows:
                commons.append(person)
        return commons
    

    def get_line_dfs(self, user_id, target, line):
        pass

    def get_line_bfs(self, user_id, target, line):
        pass

    def get_all_weibo(self, user_id):
        res = self._session.get(url='https://weibo.cn/u/{}'.format(user_id))
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        page = None

        try:
            pagelist = soup.find(id='pagelist')
            page = int(pagelist.findAll('input')[0].get('value'))
        except Exception:
            page = 1

        weibos = []
        for i in range(1, page + 1):
            res = self._session.get(url='https://weibo.cn/u/{}?page={}'.format(user_id, i))
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            # 手机微博触屏版
            # 最后两个也是信息
            cs = soup.findAll('div', attrs={'class': 'c'})[1:-2]
            for c in cs:
                print(c)
                break
            break


    
if __name__ == '__main__':
    obj = weibo()
    obj.login()
    # print(obj.get_fans('2667215760'))
    print(obj.get_all_weibo(''))
    
    
