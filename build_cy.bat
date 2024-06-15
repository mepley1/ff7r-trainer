@echo off

echo Moving any Cython built modules from root dir to /app ...
move ".\*.*.pyd" ".\app"

echo Beginning build ...

pyinstaller --onefile ^
    --clean ^
    --noconsole ^
    --add-data=".\assets\ff7r.png;assets" ^
    --icon=".\assets\icon-p2.ico" ^
    --name="TRAiNER" ^
    .\app\launch.py
