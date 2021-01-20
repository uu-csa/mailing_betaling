@echo off
@echo.
@echo  * activate virtual environment
call venv\Scripts\activate.bat
@echo  * run app
@echo.
@echo --------------------------------------------------------------------------
call python.exe app.py
timeout /t 30
