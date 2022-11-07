import asyncio
import time
import os
import multiprocessing
import concurrent.futures
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

# Timeout: total = total time for connection all proxies (in s.)
#          connect = time to connect each of the proxies (in s.)
TIMEOUT = aiohttp.ClientTimeout(total=300, connect=5)
LINK = 'https://2ip.ru'

unchecked_proxies_file = os.path.join(os.getcwd(), 'data', 'proxies.txt')
checked_proxies_dir = os.path.join(os.getcwd(), 'data')

with open(unchecked_proxies_file, 'r') as prox:
    modified_proxy = list()
    proxies = ''.join(prox.readlines()).strip().split('\n')
    for proxy in proxies:
        proxy_params = proxy.split(':')
        usefully_proxy_params = f'http://{proxy_params[2]}:{proxy_params[3]}@{proxy_params[0]}:{proxy_params[1]}'
        modified_proxy.append(usefully_proxy_params)


async def check_proxy(array_proxies, url):
    date_time = datetime.now().strftime('%d.%m.%Y_%H:%M')

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=TIMEOUT) as session:
            async with session.get(url, proxy=array_proxies) as resp:
                body = await resp.text()
                soup = BeautifulSoup(body, 'lxml')

                ip = soup.find('div', class_='ip').text.strip()
                loc = soup.find('div', class_='value-country').text.strip()

                print(f'{ip}\n{loc}\n')

                with open(os.path.join(checked_proxies_dir, f'checked_proxy_{date_time}.txt'), 'a') as checked:
                    pre_proxy = proxy.replace('http://', '').split('@')[::-1]
                    original_proxy = ':'.join(pre_proxy)
                    checked.write(f'{original_proxy}\n')

    except Exception as ex:
        with open(os.path.join(checked_proxies_dir, f'log_{date_time}.txt'), 'a') as log:
            log.write(f'\n[PROXY]: {array_proxies}\n[ERROR]: {ex}\n' + '-' * 192)

    await asyncio.sleep(.15)


def get_and_output(params, url):
    asyncio.run(check_proxy(params, url))


def main() -> None:
    strt = time.time()
    num_cores = multiprocessing.cpu_count()

    futures = []
    length_data = len(modified_proxy)

    with concurrent.futures.ProcessPoolExecutor(num_cores) as executor:
        for i_prox in modified_proxy:
            new_future = executor.submit(
                get_and_output,
                params=i_prox,
                url=LINK
            )
            futures.append(new_future)
            length_data -= 1

    concurrent.futures.wait(futures)
    stp = time.time()
    print(stp-strt)


if __name__ == '__main__':
    main()
