import threading

from src.util import Config, Request, DB, Logger


def pool_lock(func):
    def wrapper(*arg, **kwargs):
        with ProxyPool._instance_lock:
            return func(*arg, **kwargs)

    return wrapper


class ProxyPool(Request):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(ProxyPool, "_instance"):
            with ProxyPool._instance_lock:
                if not hasattr(ProxyPool, "_instance"):
                    ProxyPool._instance = object.__new__(cls)
        return ProxyPool._instance

    def __init__(self):
        super(ProxyPool, self).__init__()
        self.config = Config().config
        self.default_db = DB().default_db
        self.proxy_db = DB().proxy_db
        self.logger = Logger().logger

    def _fetch_proxy_http_1(self):
        url = 'http://www.ip3366.net/free/?stype=1'
        soup = self.get_soup(url)
        for tr in soup.find_all('tr')[1:]:
            ip, port = map(lambda x: x.text, tr.find_all('td')[0:2])
            self.default_db.hset('HTTP', ip, port)

    def _fetch_proxy_http_2(self):
        url = 'https://www.xicidaili.com/wt/'
        soup = self.get_soup(url)
        for tr in soup.find_all('tr')[1:]:
            ip, port = map(lambda x: x.text, tr.find_all('td')[1:3])
            self.default_db.hset('HTTP', ip, port)

    def _fetch_proxy_https_1(self):
        url = 'http://www.ip3366.net/free/?stype=2'
        html = self.get(url)
        soup = self.res2soup(html)
        for tr in soup.find_all('tr')[1:]:
            ip, port = map(lambda x: x.text, tr.find_all('td')[0:2])
            self.default_db.hset('HTTPS', ip, port)

    def _fetch_proxy_https_2(self):
        url = 'https://www.xicidaili.com/wn/'
        soup = self.get_soup(url)
        for tr in soup.find_all('tr')[1:]:
            ip, port = map(lambda x: x.text, tr.find_all('td')[1:3])
            self.default_db.hset('HTTPS', ip, port)

    @pool_lock
    def delete_backup_proxy(self):
        _ = [self.default_db.hdel('HTTP', key) for key in self.default_db.hkeys(name='HTTP')]
        _ = [self.default_db.hdel('HTTPS', key) for key in self.default_db.hkeys(name='HTTPS')]

    @pool_lock
    def delete_valid_proxy(self):
        _ = [self.proxy_db.delete(key) for key in self.proxy_db.keys()]

    @pool_lock
    def _delete_all_proxy(self):
        _ = [self.default_db.hdel('HTTP', key) for key in self.default_db.hkeys(name='HTTP')]
        _ = [self.default_db.hdel('HTTPS', key) for key in self.default_db.hkeys(name='HTTPS')]
        _ = [self.proxy_db.delete(key) for key in self.proxy_db.keys()]

    def _fetch_proxy(self, type):
        if type == 'HTTP':
            self._fetch_proxy_http_1()
            self._fetch_proxy_http_2()
        if type == 'HTTPS':
            self._fetch_proxy_https_1()
            self._fetch_proxy_https_2()

    def _check_proxy(self, ip, port, timeout=3):
        if not ip or not port:
            return False
        http_url = 'http://{}:{}'.format(ip, port)
        https_url = 'https://{}:{}'.format(ip, port)
        try:
            self.get(url="http://icanhazip.com/", timeout=timeout, proxies={'http': http_url, 'https': https_url})
            return True
        except:
            return False

    def _get_backup_proxy(self, type='HTTPS'):
        import random
        ip = random.choice(self.default_db.hkeys(type))
        port = self.default_db.hget(type, ip)
        return ip, port

    def _get_valid_proxy(self, type='HTTPS', seed_num=1):
        for _ in range(len(self.default_db.hkeys(type))):
            ip, port = self._get_backup_proxy(type)
            if self._check_proxy(ip, port):
                self.logger.info('backup ip {} valid, fetch'.format(ip))
                self.proxy_db.set(ip, port, ex=3600)
                if len(self.proxy_db.keys()) >= seed_num:
                    break
            else:
                self.logger.info('backup ip {} invalid, delete'.format(ip))
                self.default_db.hdel(type, ip)
                pass
        else:
            self.logger.info('no enough {} backup valid ip'.format(seed_num))
            pass

    @pool_lock
    def get_proxy(self, type='HTTPS', seed_num=1, distinct=False):
        if len(self.proxy_db.keys()) == 0:
            self.logger.info('no valid proxy in proxy pool')
            if not self.default_db.exists(type) or not len(self.default_db.hkeys(type)):
                self.logger.info('no backup {} proxy, fetch from web'.format(type))
                self._fetch_proxy(type)
                self.logger.info('fetch ok, {} items in total'.format(len(self.default_db.hkeys(type))))
            self.logger.info('fetch valid proxy from backup proxy pool')
            self._get_valid_proxy(type, seed_num)
            assert len(self.proxy_db.keys()) != 0
            self.logger.info('fetch valid proxy ok')

        ip = self.proxy_db.keys()[0]
        port = self.proxy_db.get(ip)
        if distinct:
            self.proxy_db.delete(ip)
            self.default_db.hdel(type, ip)
        else:
            pass
        return ip, port

    @pool_lock
    def delete_proxy(self, ip, type='HTTPS'):
        self.proxy_db.delete(ip)
        self.proxy_db.hdel(type, ip)


if __name__ == '__main__':
    obj1 = ProxyPool()
