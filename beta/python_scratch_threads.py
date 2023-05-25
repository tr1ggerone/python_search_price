# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:27:46 2023

@author: HuangAlan
"""
import requests
import numpy as np
from bs4 import BeautifulSoup
import colorama
from colorama import Fore
from colorama import Style
from concurrent.futures import ThreadPoolExecutor
from time import time

# %% scratch
def get_price(page):
    global flag_ana
    
    # ----- search in ruten -----
    url_p = url + '&p=' + str(page)
    web = requests.get(url_p, headers=headers)
    soup = BeautifulSoup(web.text, 'html.parser')
    page_item = soup.select('.product-item')
    if page_item == []:
        return
    try:
        if soup.find('p', class_='rt-mt-3x').get_text():
            print('no search result')
            flag_ana = False
        return
    except AttributeError:
        pass
        
    # ----- list item in each page -----
    for i_item in page_item:
        try:
            _title = i_item.find('p', class_='rt-product-card-name').get_text().lower()
            _price = i_item.find('div', class_='rt-product-card-price-wrap').get_text()
            _link = i_item.find('a')['href']
            try:
                _sale = i_item.find_all('div',class_='rt-product-card-sold')[0].get_text()
                _sale = _sale.split(' ')[-1]
            except:
                _sale = '0'
            table_price.append([_title.strip(), _price.strip(), _sale, _link])
        except AttributeError:
            pass

# %% scratch
if __name__ == "__main__":
    
    # ----- initial -----
    colorama.init()
    error_log = []
    BANNED = np.genfromtxt('banned_keyword.txt', dtype='U20', encoding='utf-8')

    while True:
        item_name = input(Fore.CYAN + Style.BRIGHT + '<<< item name: ' + Style.RESET_ALL)
        if item_name == str():
            break
        
        # ----- search in ruten -----
        _time_start = time()
        url = 'https://www.ruten.com.tw/find/?q='+item_name
        headers = {'User-Agent':'GoogleBot'}
        table_price = []
        MAX_PAGE = 50
        flag_ana = True
    
        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(get_price, (page for page in range(1, MAX_PAGE)))
        print('time consumed in searching: %.4f' %(time()-_time_start))
    
    

