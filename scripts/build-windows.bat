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
echo Generated files
echo ---------------
dir dist\cleepbus

echo.
echo.
echo Getting version
echo ---------------
cd dist\cleepbus
$VERSION=.\cleepbus.exe --version > version.txt
echo "Found version $VERSION"

echo.
echo.
echo Packaging application...
echo ------------------------
Compress-Archive * "../cleepbus-v$VERSION-windows-x64.zip"
if %ERRORLEVEL% NEQ 0 goto :error
echo Package build successfully

cd ..\..

goto :success

:error
echo.
echo.
echo ===== Error occured see above =====
goto :end

:success
echo.
echo.
echo Build successful
goto :end

:end
