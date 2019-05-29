from src.core import Brisk


class Crawler(Brisk):
    def hook(self):
        self.logger.info('I AM HOOK')

    def flow_1(self):
        self.get('http://httpbin.org/get').text

    def flow_2(self):
        payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
        self.get('http://httpbin.org/get', params=payload).text

    def flow_3(self):
        payload = {'key': 'value'}
        self.post('http://httpbin.org/post', data=payload).text

    def flow_4(self):
        self.get_json('https://api.github.com/events')


if __name__ == '__main__':
    obj = Crawler()
    obj.go()
