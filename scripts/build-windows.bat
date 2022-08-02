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
xcopy /q /y config\windows.spec pyinstaller.spec
py -3 -m PyInstaller --clean --noconfirm --windowed --log-level INFO pyinstaller.spec
if %ERRORLEVEL% NEQ 0 goto :error
del /q pyinstaller.spec

echo.
echo.
echo Generated files
echo ---------------
dir dist\cleepdesktopcore

echo.
echo.
echo Getting version
echo ---------------


goto :success

:error
echo ===== Error occured see above =====

:success
