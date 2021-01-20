@echo off
@echo.
@echo  * activate virtual environment
call conda activate betaalmail
@echo  * run app
@echo.
@echo --------------------------------------------------------------------------
call python.exe app.py
timeout /t 30
