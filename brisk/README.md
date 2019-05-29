# brisk

[config](./config.ini)

```
[TOKEN]						# 验证信息

[PROXY]						# 代理选项
use = TRUE					# 是否使用代理
empty = TRUE					# 代理是否初始清空
seed_num = 6					# 预备代理数量
distinct = TRUE					# 代理是否重复使用
type = HTTPS					# 代理类型

[DB]						# 数据库选项
type = REDIS					# 默认使用redis

[LOG]						# 输出日志格式选项
format = DEFAULT			

[RUN]						# 运行选项
type = FLOW					# 串行 or 并行
timeout = 5					# 超时阈值
num = 2						# 最大支持并行数
```

api

```python
@property 
Brisk.headers Brisk.cookies Brisk.session

@abstractmethod 
Brisk.get_token() Brisk.set_token() Brisk.refresh_token() Brisk.clear_token()

Brisk.get(self, url, params=None, **kwargs)
Brisk.post(self, url, data, **kwargs)
Brisk.get_soup(self, url, params=None, **kwargs)
Brisk.get_json(self, url, params=None, **kwargs)
```

serial demo


```python
from core import Brisk


class Crawler(Brisk):
    def hook(self):
        self.logger.info('I AM HOOK')

    def walk_1(self):
        self.logger.info(self.get('http://httpbin.org/get').text)

    def walk_2(self):
        payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
        self.logger.info(self.get('http://httpbin.org/get', params=payload).text)

    def walk_3(self):
        payload = {'key': 'value'}
        self.logger.info(self.post('http://httpbin.org/post', data=payload).text)

    def walk_4(self):
        self.logger.info(self.get_json('https://api.github.com/events'))


if __name__ == '__main__':
    obj = Crawler()
    obj.go()
```

[parallel demo](./demo.py)


```python
from core import Brisk


class Crawler(Brisk):
    def hook(self):
        self.logger.info('I AM HOOK')

    def flow_1(self):
        self.logger.info(self.get('http://httpbin.org/get').text)

    def flow_2(self):
        payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
        self.logger.info(self.get('http://httpbin.org/get', params=payload).text)

    def flow_3(self):
        payload = {'key': 'value'}
        self.logger.info(self.post('http://httpbin.org/post', data=payload).text)

    def flow_4(self):
        self.logger.info(self.get_json('https://api.github.com/events'))


if __name__ == '__main__':
    obj = Crawler()
    obj.go()
```
