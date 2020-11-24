from time import mktime, localtime, time, strptime, strftime
from random import choice, choices, randint, uniform, _urandom
from string import ascii_letters, digits
from urllib.parse import ParseResult

from .cc_constant import acceptall, referers, cookies, post_data


def random_url():
    return ''.join(choices(ascii_letters + digits, k=25))


def random_date() -> str:
    timeint = uniform(mktime(strptime("2020", "%Y")), time())
    return strftime("%Y%m%d", localtime(timeint))


def gen_header(method, target_url: ParseResult):
    connection = 'Connection: Keep-Alive\r\n'
    language = 'Accept-language: en-US,en,q=0.5\r\n'
    user_agent = f'User-Agent: {get_useragent()}\r\n'
    accept = choice(acceptall)
    cookies_header = ''
    extra_header = ''
    if cookies:
        cookies_header = f'Cookies: {cookies}\r\n'
    if method == "get" or method == "head":
        add = "?"
        if target_url.query:
            add = "&"
        if method == 'get':
            method_str = "GET"
        elif method == 'head':
            method_str = "HEAD"
        method_header = f'{method_str} {target_url.path}{add}{random_url()} HTTP/1.1\r\n'
        host_header = f'Host: {target_url.hostname}\r\n'
        referer = "Referer: " + choice(referers) + target_url.geturl() + "\r\n"
    elif method == "post":
        method_header = f'POST {target_url.path} HTTP/1.1\r\n'
        host_header = f'Host: {target_url.path}\r\n'
        referer = "Referer: " + target_url.geturl() + "\r\n"
        content = "Content-Type: application/x-www-form-urlencoded\r\n"\
            + "X-requested-with:XMLHttpRequest\r\n"
        if post_data:
            data = post_data
        else:
            data = _urandom(16)
        length = f'Content-Length: {len(data)}\r\n'
        extra_header = content + length
    elif method == 'slow':
        method_header = f'GET /?{randint(0, 2000)} HTTP/1.1\r\n'
        host_header = ''
        referer = ''
    return method_header + host_header + accept \
        + language + connection + user_agent + referer + cookies_header \
        + extra_header + "\r\n\r\n"


def get_useragent():
    platform = choice(['Macintosh', 'Windows', 'X11'])
    if platform == 'Macintosh':
        os = choice(['68K', 'PPC', 'Intel Mac OS X'])
    elif platform == 'Windows':
        os = choice([
            'Win3.11', 'WinNT3.51', 'WinNT4.0', 'Windows NT 5.0',
            'Windows NT 5.1', 'Windows NT 5.2', 'Windows NT 6.0',
            'Windows NT 6.1', 'Windows NT 6.2', 'Win 9x 4.90', 'WindowsCE',
            'Windows XP', 'Windows 7', 'Windows 8',
            'Windows NT 10.0; Win64; x64'
        ])
    elif platform == 'X11':
        os = choice(['Linux i686', 'Linux x86_64'])
    browser = choice(['chrome', 'firefox', 'ie'])
    if browser == 'chrome':
        webkit = randint(500, 599)
        version = f'{randint(0, 99)}.0{randint(0, 9999)}.{randint(0, 999)}'
        return 'Mozilla/5.0 (' + os + ') AppleWebKit/' \
            + f'{webkit}.0 (KHTML, like Gecko) Chrome/' \
            + f'{version} Safari/{webkit}'
    elif browser == 'firefox':
        gecko = random_date()
        version = str(randint(1, 72)) + '.0'
        return 'Mozilla/5.0 (' + os + '; rv:' + version + ') Gecko/'\
            + gecko + ' Firefox/' + version
    elif browser == 'ie':
        version = str(randint(1, 99)) + '.0'
        engine = str(randint(1, 99)) + '.0'
        option = choice([True, False])
        if option:
            token = choice([
                '.NET CLR', 'SV1', 'Tablet PC', 'Win64; IA64', 'Win64; x64',
                'WOW64'
            ]) + '; '
        else:
            token = ''
        return 'Mozilla/5.0 (compatible; MSIE '\
            + version + '; ' + os + '; ' + token + 'Trident/' + engine + ')'
