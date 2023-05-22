# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:27:46 2023

@author: HuangAlan
"""
__version__='0.1.0'
from datetime import date
import logging
import re
from time import time
from bs4 import BeautifulSoup
import colorama
from colorama import Fore
from colorama import Style
import numpy as np
import pandas as pd
import requests

# %% initial
# ----- initial para -----
colorama.init()
BANNED = np.genfromtxt('banned_keyword.txt', dtype='U20', encoding='utf-8')

# ----- set logger -----
# level set as bebug, will recorded the http debug message in .log
logging.basicConfig(level=logging.INFO, filename= f'search-{date.today()}.log', 
                    format='%(asctime)s, %(levelname)s: %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')
    
# %% scratch
while True:
    item_name = input(Fore.CYAN + Style.BRIGHT +
                      '<<< 請輸入卡片編號/名稱/型號: ' + 
                      Style.RESET_ALL)
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
    
    # ----- select search result in each page -----
    logging.info('[%s] strat searching...' % item_name)
    for page in range(1, MAX_PAGE):
        url_p = url + '&p='+str(page)
        web = requests.get(url_p, headers=headers)
        # soup = BeautifulSoup(web.text, 'html5lib')
        soup = BeautifulSoup(web.text, 'html.parser')
        page_item = soup.select('.product-item')
        if page_item == []:
            break
        try:
            if soup.find('p', class_='rt-mt-3x').get_text():
                logging.warning('[%s] cannot search the result' % item_name)
                print('很抱歉查詢不到符合的商品，請更換關鍵字後再試\n')
                flag_ana = False
            break
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
    logging.info('[%s] search time: %.2f sec.' % (item_name, time()-_time_start))
    
    # %% summary result
    if flag_ana:
        
        # ----- pre process -----
        item_key = item_name.split(' ')
        table_price = pd.DataFrame(np.array(table_price), 
                                   columns = ['name', 'price', 'sales', 'link'])
        
        # ----- select result -----
        table_summary = []
        table_summary_ban = []
        for i_idx in range(len(table_price)):
            _tmp = table_price.loc[i_idx,:]
            if all([True if i.lower() in _tmp['name'] else False for i in item_key]):
                
                # ---- decoding price -----
                flag_banned = False
                if '~' in _tmp['price']:
                    _price =  _tmp['price']
                    flag_banned = True
                elif '約' in _tmp['price']:
                    _price = re.sub(',', '', _tmp['price'].split('約')[-1].strip())
                    _local = '海外'
                else:
                    _price = re.sub(',', '',  _tmp['price'])
                    _local = '國內'
                _n, _c = np.unique(re.findall('\d', _price), return_counts=True)
                
                # ----- check -----
                _tmp_df = [_tmp['name'], _price, _tmp['sales'], _local, _tmp['link']]
                if list(filter(lambda x: x in _tmp_df[0], BANNED)) or flag_banned:
                    table_summary_ban.append(_tmp_df)
                elif len(_n) == 1 and _c[0] >= 5:
                    table_summary_ban.append(_tmp_df)
                elif len(re.findall('\d', _price)) >= 7:
                   table_summary_ban.append(_tmp_df) 
                else:
                    table_summary.append(_tmp_df)

        # ----- decoding to dataframe -----
        flag_list = True
        try:
            COL = ['name', 'price', 'sales', 'local', 'link']
            if len(table_summary_ban) > 0:
                table_summary_ban = pd.DataFrame(np.array(table_summary_ban),
                                                 columns = COL)
            table_summary = pd.DataFrame(np.array(table_summary),
                                         columns = COL)
            table_summary = table_summary.astype({'price': 'int32',
                                                  'sales': 'int32'})
        except:
            logging.error('[%s] cannot decoding the table_summary' % item_name)
            print('無滿足關鍵字之條件，請更換其它附帶關鍵字\n')
            flag_list = False
        
        # ----- list reference -----
        if flag_list:
            for i_local in ['國內', '海外']:
                _tmp_table = table_summary.loc[
                    table_summary['local']==i_local].sort_values('price')
                
                if len(_tmp_table) != 0:
                    _table_q1 = _tmp_table["price"].quantile(0.25)
                    _table_med = _tmp_table["price"].median()
                    _table_top_n = _tmp_table.iloc[:3,:]
                    if i_local == '國內':
                        recmd_price = int(np.round(_table_q1*0.8,-2))
                        logging.info('[%s] purchase/selling price: %d NTD' 
                                     % (item_name, recmd_price))
                        
                        print(Fore.CYAN + Style.BRIGHT +
                              '<<< ---------系統建議售(收)價:' + 
                              Style.RESET_ALL + f' {recmd_price} NTD')
                        
                        print(Fore.YELLOW + Style.BRIGHT +
                              f'{i_local}售價中位數: {int(_table_med)}'+ 
                              f', 售價第一位數: {int(_table_q1)}' +
                              Style.RESET_ALL)
                        
                    print(Fore.YELLOW + Style.BRIGHT +
                          f'{i_local}售價前三低的價格與連結:' + 
                          Style.RESET_ALL)
                    print(_table_top_n.loc[:,['name', 'price', 'sales', 'link']].to_markdown())
                    print('')


