# python search card price
- python 版本為3.9.7 

## 功能說明
1. 依照輸入卡號迴傳露天拍賣上前三便宜的卡價、銷售數量與連結
2. 分別列出國內與海外的結果
3. 搜尋結果將會存成log檔，並依照日期命名與儲存
4. 要禁止的關鍵字可加在`banned_keyword.txt`中，搜尋結果便會給與排除

## 使用流程
- 建立virtual env並安裝相對應的python package，以下為Anaconda Prompt的範例
```
conda create -n web_env python=3.9.7
conda activate web_env
pip install -r requirements.txt
```
- 創建完環境後，便可輸入**python python_scratch.py**啟動查詢程式
- 若要關閉程式可直接按下`Enter鍵`，便會自動關閉程式
- 要查詢當天的歷史收尋紀錄可以到**search.log**中查看

## 參考資料
- [beautiful soup 實作](https://steam.oxxostudio.tw/category/python/spider/beautiful-soup.html)
- [露天爬蟲參考]https://tlyu0419.github.io/2020/06/14/Crawler-Ruten/
- [logging 官方文檔]https://docs.python.org/zh-tw/3/howto/logging.html#handler-basic