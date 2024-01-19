REM use anaconda3\Scripts\activate.bat to activate anaconda prompt
REM run.bat version: 0.1.2

call %USERPROFILE%\anaconda3\Scripts\activate.bat
call conda info --envs | findstr "\<web_env\>" > nul
if not errorlevel 1 (
    echo env is existed...
	call conda activate web_env
) else (
    echo setup web_env...
	call conda create -n web_env python=3.9.7
	call conda activate web_env
	call pip install -r setting/requirements.txt
)
python python_scratch.py
pause
