@echo off

echo ######## Copying .py files to .pyx ... ########
if not exist .\tmp\NUL mkdir .\tmp
copy ".\app\gui.py" ".\tmp\gui.pyx"
copy ".\app\offsets.py" ".\tmp\offsets.pyx"
copy ".\app\settings.py" ".\tmp\settings.pyx"
copy ".\app\launch.py" ".\tmp\launch.py"

echo ######## Running setup (Cython build) ... ########
python setup_auto.py build_ext --inplace

echo ######## Moving Cython built modules from root dir to /tmp ... ########
move ".\*.*.pyd" ".\tmp"

echo ######## Beginning pyinstaller build ... ########

pyinstaller --onefile ^
    --clean ^
    --noconsole ^
    --add-data=".\assets\ff7r.png;assets" ^
    --icon=".\assets\icon-p2.ico" ^
    --name="TRAiNER" ^
    .\tmp\launch.py

echo ######## Copying ff7r.png to .\dist ... ########
if not exist .\dist\assets\NUL mkdir .\dist\assets
copy ".\assets\ff7r.png" ".\dist\assets\ff7r.png"

::echo ######## Clearing /tmp dir ... ########
::del ".\tmp\*"

echo ######## FINISHED ########
