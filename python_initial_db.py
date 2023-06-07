# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 11:52:13 2023

@author: HuangAlan
"""
__version__ = '0.1.0'
import pymysql
import json

# %% main
# ----- load config -----
with open('config.json',encoding='utf-8') as file:
    config = json.load(file)

# ----- initial db -----
db_settings = dict(host='127.0.0.1', # ipv4 of database
                   port=3306,
                   user=config['user'],
                   passwd=config['passwd'],
                   charset='utf8')
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
    # ----- close the connect with database -----
    conn.close()