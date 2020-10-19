@echo off
@echo.
@echo  * activate virtual environment 'osiris-query'
REM call activate osiris-query
call venv\Scripts\activate.bat
@echo  * run app
@echo.
@echo --------------------------------------------------------------------------
call python.exe app_test.py
pause
