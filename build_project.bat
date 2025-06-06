rem Установить следующие пакеты:
rem     pip install pyinstaller
rem     pip install pyinstaller_versionfile



@echo off

cd build_misc/

python version_updater.py

echo -----

create-version-file ^
    metadata.yml ^
    --outfile file_version_info.txt

cd ..

pyinstaller ^
    -F ^
    -w main.py ^
    --add-data "img/*;./img" ^
    --add-data "icon/*;./icon" ^
    --workpath ./ ^
    -i icon/icon.ico ^
    --version-file build_misc/file_version_info.txt ^
    -n RomashkiDimensions.exe

    rem --clean ^

del .\build_misc\file_version_info.txt

pause

