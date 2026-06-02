@echo off
cd /d "%~dp0"
echo Iniciando Normal Map Generator...
echo.

:: Buscar python.exe en ubicaciones comunes
set PYTHON=

for %%P in (
    "C:\Python314\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
) do (
    if exist %%P (
        set PYTHON=%%P
        goto :found
    )
)

:: Intentar con el PATH del sistema
where python >nul 2>&1 && set PYTHON=python && goto :found
where py >nul 2>&1 && set PYTHON=py && goto :found

echo ERROR: No se encontro Python instalado.
echo Instala Python desde https://www.python.org
echo.
pause
exit /b 1

:found
echo Usando Python: %PYTHON%
echo.
%PYTHON% "%~dp0normal_generator.py"

echo.
echo --- Cerrado. Si hubo error, leelo arriba ---
pause
