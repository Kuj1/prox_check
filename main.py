#!/usr/bin/env python3

import asyncio
import warnings
import os
from datetime import datetime

import aiohttp
import requests
from bs4 import BeautifulSoup

API_KEY = '9csvVU6SRe4D4vlzkglWIiNQwbcrva4w'

warnings.filterwarnings("ignore", category=DeprecationWarning) 

unchecked_proxies_file = os.path.join(os.getcwd(), 'data', 'proxies.txt')
checked_proxies_dir = os.path.join(os.getcwd(), 'data')

def modify_proxy(path_to_proxy):
    modified_proxy = set()
    with open(path_to_proxy, 'r') as prox:
        for proxy in prox.readlines():
            proxy_params = proxy.replace('\n', '').split(':')
            usefull_proxy = f'http://{proxy_params[2]}:{proxy_params[3]}@{proxy_params[0]}:{proxy_params[1]}'
            modified_proxy.add(usefull_proxy)
    
    return modified_proxy


async def check_proxy_api(api_key, proxy_list):
    modified_proxys = modify_proxy(proxy_list)
    for proxy in modified_proxys:
        usefull_proxy = proxy.replace('http://', '').split('@')[::-1][0].split(':')[0]


        # resp = requests.get(f'https://ipqualityscore.com/api/json/ip/{api_key}/{usefull_proxy}')
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                # print(f'https://ipqualityscore.com/api/json/ip/{api_key}/{proxy}')
                async with session.get(f'https://ipqualityscore.com/api/json/ip/{api_key}/{usefull_proxy}') as resp:
                    if resp.status == 200:
                        body = await resp.json()
                        print(body['fraud_score'])
                    else:
                        print(resp.status)
            except Exception as ex:
                print(ex)
        

async def check_proxies(url):
    proxies = modify_proxy(unchecked_proxies_file)

    date_time = datetime.now().strftime('%d.%m.%Y_%H:%M')

    for proxy in proxies:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                async with session.get(url, proxy=proxy) as resp:
                    if resp.status == 200:
                        print('OK')
                        body = await resp.text()
                        soup = BeautifulSoup(body, 'lxml')
                        # print(soup)

                        ip = soup.find('div', class_ = 'ip').text.strip()
                        loc = soup.find_all('div', class_='value-country').text.strip()

                        print(f'{ip}\n{loc}\n')

                        with open(os.path.join(checked_proxies_dir, f'checked_proxy_{date_time}.txt'), 'a') as checked:
                            pre_proxy = proxy.replace('http://', '').split('@')[::-1]
                            original_proxy = ':'.join(pre_proxy)
                            checked.write(f'{original_proxy}\n')
                    else:
                        print(f'{resp.status}')



            except Exception as ex:
                    with open(os.path.join(checked_proxies_dir, f'log_{date_time}.txt'), 'a') as log:
                        log.write(f'\n[PROXY]: {proxy}\n[ERROR]: {ex}\n' + '-' * 192)

if __name__ == '__main__':
    asyncio.run(check_proxy_api(api_key=API_KEY, proxy_list=unchecked_proxies_file))
    # url = 'https://2ip.ru'

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # future = asyncio.ensure_future(check_proxies(url=url))
    # loop.run_until_complete(future)

