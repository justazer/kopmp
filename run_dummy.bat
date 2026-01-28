@echo off
cd /d "%~dp0..\.."
echo [INFO] CWD: %CD%

echo [INFO] Running python via WSL Ubuntu...
wsl -d Ubuntu bash -c "cd /mnt/c/Users/1236/Documents/Project/Dev-Frappe-Local/frappe-bench && source env/bin/activate && python apps/kopmp/kopmp/populate_dummy_data.py"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Execution failed with code %ERRORLEVEL%.
)

echo.
echo Done.
pause
