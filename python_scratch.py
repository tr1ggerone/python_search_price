# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:27:46 2023

@author: Aaron_Huang
"""
__version__='0.3.0'
import json
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
import pymysql
import requests

# %% initial
# ----- initial para -----
os.system('cls') # need this to ensure the colorama is work in input
init(wrap=True, autoreset=True) # need to add wrap to show color in cmd

# ----- set logger -----
# level set as bebug, will recorded the http debug message in .log
logging.basicConfig(level=logging.INFO, filename= 'setting/search.log', 
                    format='%(asctime)s, %(levelname)s: %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

# ----- load config -----
with open('setting/config.json',encoding='utf-8') as file:
    config = json.load(file)
BANNED = config['banned']

# ----- connect to mySQL db -----
db_settings = dict(host='127.0.0.1', # ipv4 of database
                   port=3306,
                   user=config['user'],
                   passwd=config['passwd'],
                   database=config['schema_name'], # name of database
                   charset='utf8')

# ----- initial db -----
try:
    conn = pymysql.connect(**db_settings)
    with conn.cursor() as cursor:
        
        # ----- setup schemas -----
        schema_name = config['schema_name']
        cursor.execute('SHOW DATABASES LIKE %s', (schema_name,))
        result = cursor.fetchone()
        if not result:
            cursor.execute(f'CREATE DATABASE {schema_name}')
            print('Database created successfully!')
        else:
            print('Database already exists!')
except Exception as e:
    print(e)
finally:
    conn.close()

# ----- setup table -----
conn = pymysql.connect(**db_settings)
with conn.cursor() as cursor:
    table_name = 'ruten_price'
    cursor.execute('SHOW TABLES LIKE %s', (table_name,))
    result = cursor.fetchone()
    if not result:
        create_query = f'''CREATE TABLE {table_name} (
                            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            card_id VARCHAR(100),
                            type VARCHAR(255),
                            sug_price VARCHAR(25),
                            ref1_price VARCHAR(25),
                            ref2_price VARCHAR(25),
                            ref3_price VARCHAR(25),
                            ref1_link TEXT,
                            ref2_link TEXT,
                            ref3_link TEXT)'''
        cursor.execute(create_query)
        conn.commit()
    
# %% scratch
while True:
    item_name = input(Fore.CYAN + Style.BRIGHT +
                      '<<< 請輸入卡片編號/名稱/型號: ' + Style.RESET_ALL)
    if item_name == str():
        logging.info('結束搜尋')
        conn.close()
        break
    BANNED = [i for i in BANNED if i not in item_name]
    # print(BANNED)
    
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
    # print(table_price)

    # %% summary result
    if flag_ana:
        
        # ----- pre-process -----
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
                    _price =  re.sub(',', '',  _tmp['price'].split('~')[0])
                    flag_banned = True
                elif '約' in _tmp['price']:
                    _price = re.sub(',', '', _tmp['price'].split('約')[-1].strip())
                    _local = '海外'
                elif ' ' in _tmp['price']:
                    _price = re.sub(',', '',  _tmp['price'].split(' ')[0])
                    _local = '國內(降價)'
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
        except Exception as e:
            logging.error('Cannot decoding the table_summary. Error: {}'.format(e))
            print('無滿足關鍵字之條件，請更換其它附帶關鍵字\n')
            flag_list = False
        
        # ----- transfer data type -----
        try:
            table_summary = table_summary.astype({'price': 'int32', 'sales': 'int32'})
        except Exception as e:
            logging.error('Failed to convert data type in pandas. Error: {}'.format(e))
            print('轉換格式失敗\n')
            flag_list = False

        # ----- list reference -----
        if flag_list:
            i_local = '國內'
            _tmp_table = table_summary[table_summary['local'].str.contains(i_local, case=False)].sort_values('price')
            if len(_tmp_table) != 0:
                _table_q1 = _tmp_table["price"].quantile(0.25)
                _table_med = _tmp_table["price"].median()
                _table_top_n = _tmp_table.iloc[:3,:]
                recmd_price = int(np.round(_table_q1*0.8,-2))
                print(Fore.CYAN + Style.BRIGHT + '<<< 系統建議售(收)價:' + Style.RESET_ALL + f' {recmd_price} NTD')
                print(Fore.YELLOW + Style.BRIGHT + f'{i_local}售價中位數: {int(_table_med)}'+ f', 售價第一位數: {int(_table_q1)}')
                print(Fore.YELLOW + Style.BRIGHT + f'{i_local}售價前三低的價格與連結:')
                print(_table_top_n.to_markdown())
                
            # %% write into db
            # ----- generate db format data -----
            card_name = item_key[0]
            card_type = '' if len(item_key)==1 else item_key[1]
            for i, i_price, i_link in zip(range(3), 
                                          ['ref1_price', 'ref2_price', 'ref3_price'],
                                          ['ref1_link', 'ref2_link', 'ref3_link']):
                try:
                    locals()[i_price] = str(_table_top_n.iloc[i,1])
                    locals()[i_link] = _table_top_n.iloc[i,4]
                except:
                    locals()[i_price] = ''
                    locals()[i_link] = ''
            
            # ----- db part -----
            try:
                with conn.cursor() as cursor:
                    check_query = f"SELECT * FROM {table_name}"
                    cursor.execute(check_query)
                    table = cursor.fetchall()
                    
                    # ----- check card_id in db or not -----
                    check_query = f"SELECT card_id FROM {table_name} WHERE card_id=%s AND type=%s"
                    cursor.execute(check_query, (item_key[0],card_type))
                    result = cursor.fetchone()
                    
                    
                    # ----- insert/update db -----
                    if not result:
                        command = f"""INSERT INTO {table_name} (card_id, type, 
                        sug_price, ref1_price, ref2_price, ref3_price, ref1_link, 
                        ref2_link, ref3_link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        cursor.execute(command, 
                                       (card_name, card_type, str(recmd_price), 
                                        ref1_price, ref2_price, ref3_price, 
                                        ref1_link, ref2_link, ref3_link))
                        print('insert item')
                    else:
                        command = f"""UPDATE {table_name} SET card_id=%s, type=%s, 
                        sug_price=%s, ref1_price=%s, ref2_price=%s, ref3_price=%s, 
                        ref1_link=%s, ref2_link=%s, ref3_link=%s WHERE card_id=%s AND type=%s"""
                        cursor.execute(command, 
                                       (card_name, card_type, str(recmd_price), 
                                        ref1_price, ref2_price, ref3_price, 
                                        ref1_link, ref2_link, ref3_link,
                                        card_name, card_type))
                        print('update item')
                    conn.commit()
            except Exception as e:
                logging.error('database Error: {}'.format(e))
