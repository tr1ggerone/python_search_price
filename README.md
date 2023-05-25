## python search card price
- anaconda3版本: conda 4.9.1
- anaconda3版本可利用`conda -V`查詢
- anaconda3需安裝在`C:\User\your user name\`下面

## 功能說明
1. 依照輸入卡號並回傳露天拍賣上前三便宜的卡價、銷售數量與連結
2. 分別列出國內與海外的結果
3. 搜尋結果將會存成log檔，並依照日期命名與儲存
4. 要禁止的關鍵字可加在`banned_keyword.txt`中，搜尋結果便會給與排除

## 使用流程
- 為了避免`Caused by SSLError("Can't connect to HTTPS URL because the SSL module is not available."`問題，需使用virtual env來執行程式
- 將專案下載下來後，可點擊**run.bat**啟動查詢程式，以下為run.bat內code解說
``` python
call %USERPROFILE%\anaconda3\Scripts\activate.bat #啟動電腦內的anaconda3，%USERPROFILE%可自動抓取用戶資訊
call conda info --envs | findstr "\<web_env\>" > nul #判斷env是否存在，存在則啟動，不存在則創建
if not errorlevel 1 (
    echo env is existed...
    call conda activate web_env
) else (
    echo setup web_env...
    call conda create -n web_env python=3.9.7
    call conda activate web_env
    call pip install -r requirements.txt
)
python python_scratch.py #執行python script
pause
```
- 若要關閉程式可直接在查詢時按下`Enter鍵`，便會自動關閉程式
- 要查詢當天的歷史收尋紀錄可以到**search.log**中查看

## 參考資料
- [beautiful soup 實作](https://steam.oxxostudio.tw/category/python/spider/beautiful-soup.html)
- [露天爬蟲參考](https://tlyu0419.github.io/2020/06/14/Crawler-Ruten/)
- [logging 官方文檔](https://docs.python.org/zh-tw/3/howto/logging.html#handler-basic)
- [colorama顯示問題](https://lightrun.com/answers/tartley-colorama-colorama-not-working-with-input)
- [colorama教學](https://www.cnblogs.com/xiao-apple36/p/9151883.html)
