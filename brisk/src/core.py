import queue
import threading
import types

from src.proxy import ProxyPool
from src.util import Config, Request, Logger, DB


def use_proxy(func):
    def wrapper(self, *arg, **kwargs):
        if not self.proxy_ip:
            return func(self, *arg, **kwargs)
        else:
            self.logger.info('use proxy ip: {}, port: {}'.format(self.proxy_ip, self.proxy_port))
            http_url = 'http://{}:{}'.format(self.proxy_ip, self.proxy_port)
            https_url = 'https://{}:{}'.format(self.proxy_ip, self.proxy_port)
            self.proxy_format = {'proxies': {'http': http_url, 'https': https_url}}
            kwargs.update(self.proxy_format)
            return func(self, *arg, **kwargs)

    return wrapper


def load_params(func):
    def wrapper(self, *arg, **kwargs):
        timeout = int(self.config.get('RUN', 'timeout'))
        params = {'timeout': timeout}
        kwargs.update(params)
        return func(self, *arg, **kwargs)

    return wrapper


class Core(Request, threading.Thread):

    def __init__(self, queue=None):
        Request.__init__(self)
        threading.Thread.__init__(self)
        self.logger = Logger().logger
        self.config = Config().config
        self.proxy_pool = ProxyPool()
        self.__queue = queue
        self.db = DB().db
        self.proxy_ip, self.proxy_port = None, None
        self.proxy()

    def proxy(self):
        if self.config.get('PROXY', 'use') == 'TRUE':
            if not self.proxy_ip:
                self.proxy_ip, self.proxy_port = self.proxy_pool.get_proxy(
                        type=self.config.get('PROXY', 'type'), 
                        seed_num=int(self.config.get('PROXY', 'seed_num')),
                        distinct=self.config.get('PROXY', 'distinct') == 'TRUE'
                        )
            else:
                self.proxy_pool.delete_proxy(ip=self.proxy_ip, type=self.proxy_type)
                self.proxy_ip, self.proxy_port = self.proxy_pool.get_proxy(
                        type=self.config.get('PROXY', 'type'),
                        seed_num=int(self.config.get('PROXY', 'seed_num')),
                        distinct=self.config.get('PROXY', 'distinct') == 'TRUE'
                        )
        else:
            self.proxy_ip, self.proxy_port = None, None

    @use_proxy
    @load_params
    def get(self, url, params=None, **kwargs):
        return super().get(url, params, **kwargs)

    @use_proxy
    @load_params
    def post(self, url, data, **kwargs):
        return super().post(url, data, **kwargs)

    def task(self):
        pass

    def run(self):
        self.logger.info('go')
        try:
            self.task()
            self.logger.info('ok')
        except Exception as e:
            self.logger.info('something wrong')
        finally:
            if self.__queue:
                assert isinstance(self.__queue, queue.Queue)
                self.__queue.task_done()


class Brisk(Request):

    def __init__(self):
        super(Brisk, self).__init__()
        self.config = Config().config
        self.logger = Logger().logger
        self.proxy_manager = ProxyPool()
        self.db = DB().db

        self.__proxy_status = self.config.get('PROXY', 'empty')
        if self.__proxy_status == 'TRUE':
            self.proxy_manager.delete_valid_proxy()

        self.__hook_name = 'hook'
        self.__walk_name = 'walk'
        self.__flow_name = 'flow'

        self.__brisk_type = self.config.get('RUN', 'type')

        self.__func_filter = lambda m: not m.startswith("__") and \
                                       not m.startswith(self.__hook_name) and \
                                       not m.startswith(self.__walk_name) and \
                                       not m.startswith(self.__flow_name)

        self.__flow_num = int(self.config.get('RUN', 'num'))
        self.__hook = None
        self.__flow_queue = queue.Queue()
        self.__walk_queue = queue.Queue()
        self.__go_init()

    def __go_init(self):

        for method_name in list(
                filter(lambda m: m.startswith(self.__hook_name) and callable(getattr(self, m)), dir(self))):
            method = self.__class__.__dict__[method_name]
            obj = Core()
            obj.task = types.MethodType(method, obj)
            for func_name in filter(self.__func_filter, self.__class__.__dict__):
                func = self.__class__.__dict__[func_name]
                setattr(obj, func_name, types.MethodType(func, obj))
            self.__hook = obj
            break

        if self.__brisk_type == 'WALK':
            for method_name in list(
                    filter(lambda m: m.startswith(self.__walk_name) and callable(getattr(self, m)), dir(self))):
                self.__walk_queue.put(method_name)

        if self.__brisk_type == 'FLOW':
            for method_name in list(
                    filter(lambda m: m.startswith(self.__flow_name) and callable(getattr(self, m)), dir(self))):
                self.__flow_queue.put(method_name)

    def go(self):
        self.logger.info('brisk go')

        self.logger.info('brisk create {} task(s)'.format(self.__flow_queue.qsize()))
        if self.__hook:
            self.__hook_attr_base = dir(self.__hook)
            self.logger.info('brisk create hook')
            self.__hook.start()
            self.__hook.join()
            self.logger.info('brisk complete hook')

        self.__hook: Core
        self.__hook_attr = []
        for method_name in dir(self.__hook):
            if method_name not in self.__hook_attr_base:
                self.__hook_attr.append(method_name)
        while not self.__walk_queue.empty():
            method_name = self.__walk_queue.get()
            method = self.__class__.__dict__[method_name]
            t = Core(self.__walk_queue)
            for attr_name in self.__hook_attr:
                setattr(t, attr_name, self.__hook.__dict__[attr_name])
            t.task = types.MethodType(method, t)
            for func_name in filter(self.__func_filter, self.__class__.__dict__):
                func = self.__class__.__dict__[func_name]
                setattr(t, func_name, types.MethodType(func, t))
            if self.__hook:
                t.make(self.__hook.headers, self.__hook.cookies)
            t.start()
            t.join()
        self.__walk_queue.join()

        while not self.__flow_queue.empty():
            if (threading.activeCount() - 1) < self.__flow_num:
                method_name = self.__flow_queue.get()
                method = self.__class__.__dict__[method_name]
                t = Core(self.__flow_queue)
                for attr_name in self.__hook_attr:
                    setattr(t, attr_name, self.__hook.__dict__[attr_name])
                t.task = types.MethodType(method, t)
                for func_name in filter(self.__func_filter, self.__class__.__dict__):
                    func = self.__class__.__dict__[func_name]
                    setattr(t, func_name, types.MethodType(func, t))
                if self.__hook:
                    t.make(self.__hook.headers, self.__hook.cookies)
                t.start()
        self.__flow_queue.join()

        self.logger.info('brisk ok')


if __name__ == '__main__':
    obj1 = Core()
    obj2 = Core()
