from requests import get
from multiprocessing import Manager
from random import choice

socks_proxy_pages = [
    "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks{}&country=all",
    "https://www.proxy-list.download/api/v1/get?type=socks{}",
    "https://www.proxyscan.io/download?type=socks{}",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks{}.txt",
]

manager = Manager()
socks_proxy_urls = manager.list()


def download_socks(socks_version: int) -> list:
    if socks_version == 5:
        global socks_proxy_pages
        socks_proxy_pages += [
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
        ]
    for url_tem in socks_proxy_pages:
        url = url_tem.format(socks_version)
        try:
            print(f'Start to get proxy: {url}')
            with (get(url)) as r:
                for row_url in r.text.splitlines():
                    scheme = f'socks{socks_version}://'
                    if scheme not in row_url:
                        socks_proxy_urls.append(scheme + row_url)
                    else:
                        socks_proxy_urls.append(row_url)
        except Exception as e:
            print(f'Fail to get proxy: {url}, e: {e}')
    if socks_version == 4:
        try:
            print(f'Start to get proxy: {url}')
            url = "https://www.socks-proxy.net/"
            r = get(url, timeout=5)
            part = str(r.content)
            part = part.split("<tbody>")
            part = part[1].split("</tbody>")
            part = part[0].split("<tr><td>")
            for proxy in part:
                row_url_list = proxy.split("</td><td>")
                proxy = f'socks5://{row_url_list[0]}:{row_url_list[1]}'
        except Exception as e:
            print(f'Fail to get proxy: {url}, e: {e}')
    if socks_proxy_urls:
        with (open(f'socks{socks_version}.txt', 'w+')) as f:
            for url in socks_proxy_urls:
                f.writelines(url + "\n")
    print(f'> Have already downloaded socks{socks_version} proxy')
    return socks_proxy_urls


def get_random_proxy() -> str or None:
    if socks_proxy_urls:
        return choice(socks_proxy_urls)
    else:
        return None
