pyinstaller --onefile ^
    --clean ^
    --noconsole ^
    --add-data=".\assets\ff7r.png;." ^
    --icon=".\assets\icon.ico" ^
    --name="TRAINER" ^
    .\app\launch.py
