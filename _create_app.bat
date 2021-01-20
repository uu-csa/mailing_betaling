call _start_env.bat
call pyinstaller --noconfirm app.spec
timeout /t 30
