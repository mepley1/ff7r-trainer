pyinstaller --onefile ^
    --noconsole ^
    --add-data=".\assets\ff7r.png;img" ^
    --icon=".\assets\2.ico" ^
    --name="TRAINER_ff7r" ^
    .\app\gui.py
