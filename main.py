import asyncio
import time
import os
import concurrent.futures
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup


# Timeout: total = total time for connection all proxies (in s.)
#          connect = time to connect each of the proxies (in s.)
TIMEOUT = aiohttp.ClientTimeout(total=300, connect=5)

# Number of worker: the maximum number of processes
NUM_WORKERS = 10
LINK = 'https://2ip.ru'

unchecked_proxies_file = os.path.join(os.getcwd(), 'data', 'proxies.txt')
checked_proxies_dir = os.path.join(os.getcwd(), 'data')

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

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
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=TIMEOUT, headers=headers) as session:
            async with session.get(url, proxy=array_proxies) as resp:
                body = await resp.text()
                soup = BeautifulSoup(body, 'lxml')

                ip = soup.find('div', class_='ip').text.strip()

                print(f'{ip}\n{array_proxies}')

                with open(os.path.join(checked_proxies_dir, f'checked_proxy.txt'), 'a') as checked:
                    pre_proxy = array_proxies.replace('http://', '').split('@')[::-1]
                    original_proxy = ':'.join(pre_proxy)
                    checked.write(f'{original_proxy}\n')

    except Exception as ex:
        with open(os.path.join(checked_proxies_dir, f'log.txt'), 'a') as log:
            message = 'An exception of type {0} occurred.\n[ARGUMENTS]: {1!r}'.format(type(ex).__name__, ex.args)
            log.write(f'\n[DATE]: {date_time}\n[PROXY]: {array_proxies}\n[ERROR]: {ex}\n[TYPE EXCEPTION]: {message}\n' + '-' * len(message))

    await asyncio.sleep(.15)


def get_and_output(params, url):
    asyncio.run(check_proxy(params, url))


def main() -> None:
    start = time.time()
    workers = NUM_WORKERS

    futures = []
    length_data = len(modified_proxy)

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        for i_prox in modified_proxy:
            new_future = executor.submit(
                get_and_output,
                params=i_prox,
                url=LINK
            )
            futures.append(new_future)
            length_data -= 1

    concurrent.futures.wait(futures)
    stop = time.time()
    print(stop-start)


if __name__ == '__main__':
    main()
