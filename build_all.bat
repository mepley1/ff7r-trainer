:: Build full app, using the .spec file.
@echo off

echo ######## Copying .py files to .pyx ... ########
if not exist .\tmp\NUL mkdir .\tmp
copy ".\app\gui.py" ".\tmp\gui.pyx"
copy ".\app\offsets.py" ".\tmp\offsets.pyx"
copy ".\app\settings.py" ".\tmp\settings.pyx"
copy ".\app\launch.py" ".\tmp\launch.py"
copy ".\TRAiNER.spec.default" ".\TRAiNER.spec"

echo ######## Running setup (Cython build) ... ########
python setup_auto.py build_ext --inplace

echo ######## Moving Cython built modules from root dir to /tmp ... ########
move ".\*.*.pyd" ".\tmp"

echo ######## Beginning pyinstaller build ... ########

pyinstaller ^
    --clean ^
    .\TRAiNER.spec

echo ######## Copying ff7r.png to .\dist ... ########
if not exist .\dist\assets\NUL mkdir .\dist\assets
copy ".\assets\ff7r.png" ".\dist\assets\ff7r.png"

:: Uncomment to clear /tmp when finished.
::echo ######## Clearing /tmp dir ... ########
::del ".\tmp\*"

echo ######## FINISHED ########
