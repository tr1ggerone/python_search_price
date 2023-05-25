# -*- coding: utf-8 -*-
"""
Created on Thu May 25 11:16:35 2023

@author: HuangAlan
"""
__version__='0.1.1'
from datetime import date
import logging
import os
import re
from time import time
from bs4 import BeautifulSoup
from colorama import init
from colorama import Fore
from colorama import Style
import numpy as np
import pandas as pd
import requests

# %% initial
# ----- initial para -----
os.system('cls') # need this to ensure the colorama is work in input
init(wrap=True, autoreset=True) # need to add wrap to show color in cmd

# %% scratch
while True:
    item_name = input(Fore.CYAN + Style.BRIGHT +
                      '<<< 請輸入卡片編號/名稱/型號: ' + Style.RESET_ALL)
    if item_name == str():
        logging.info('結束搜尋')
        break
    
    # ----- search in ruten -----
    _time_start = time()
    url = 'https://www.ruten.com.tw/find/?q='+item_name
    headers = {'User-Agent':'GoogleBot'}
    table_price = []
    MAX_PAGE = 50
    flag_ana = True
    session = requests.session()
    
    # ----- select search result in each page -----
    logging.info('[%s] strat searching...' % item_name)
    for page in range(1, MAX_PAGE):
        url_p = url + '&p='+str(page)
        response = session.get(url_p, headers=headers)
    try:
            response = session.get(url)
            response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
            requests.exceptions.Timeout, requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException) as err_:
        logging.error("Crawling title network error: %s", err_)
        break