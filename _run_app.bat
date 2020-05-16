@echo off
@echo.
@echo  * activate virtual environment 'osiris-query'
call activate osiris-query
@echo  * run app
@echo.
@echo --------------------------------------------------------------------------
call python.exe app.py
pause