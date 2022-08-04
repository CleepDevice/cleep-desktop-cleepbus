@echo off

:: clear previous process files
rmdir /Q /S dist
rmdir /Q /S build

echo.
echo.
echo Installing dependencies...
echo --------------------------
py -3 -m pip install -r ./requirements.txt
if %ERRORLEVEL% NEQ 0 goto :error
py -3 -m pip freeze

echo.
echo.
echo Packaging application...
echo ------------------------
copy scripts\windows.spec pyinstaller.spec
py -3 -m PyInstaller --clean --log-level INFO pyinstaller.spec
if %ERRORLEVEL% NEQ 0 goto :error
del /q pyinstaller.spec

echo.
echo.
echo Getting version
echo ---------------
dist\cleepbus\cleepbus.exe --version > dist\version.txt
set /P VERSION=<version.txt
echo Found version %VERSION%
echo windows > dist\platform.txt

echo.
echo.
echo Generated files
echo ---------------
dir dist\

cd ..\..

goto :success

:error
echo.
echo.
echo ===== Error occured see above =====
exit /B 1

:success
echo.
echo.
echo Build successful

