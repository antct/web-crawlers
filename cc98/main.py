from cc98 import cc98_crawler
import argparse
from multiprocessing import Process, Queue


def parse_arguments():
    parser = argparse.ArgumentParser()
    pass
    return parser.parse_args()


if __name__ == '__main__':
    p_list = []
    p_max = 4
    for i in range(0, p_max):
        p = cc98_crawler()
        p.start()
        p_list.append(p)

    for i in p_list:
        i.join()