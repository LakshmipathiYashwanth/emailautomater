@echo off
echo ===================================================
echo 🔓 KILLING ALL CHROME PROCESSES
echo ===================================================
taskkill /F /IM chrome.exe /T
echo.
echo ===================================================
echo 🚀 LAUNCHING CHROME IN DEBUG MODE
echo ===================================================
echo.
echo Opening Chrome with Debugging on Port 9222...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --profile-directory="Profile 1" --user-data-dir="C:\Users\GLB-BLR-126\AppData\Local\Google\Chrome\User Data"
echo.
echo ⏳ Waiting 5 seconds for Chrome to initialize...
timeout /t 5
echo.
echo 🔍 CHECKING IF DEBUGGER IS ACTIVE...
curl -s http://127.0.0.1:9222/json/version
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Chrome Debugger is NOT responding on port 9222.
    echo 👉 This usually means another Chrome window is still open.
    echo 👉 Please close ALL Chrome windows and try again.
) else (
    echo.
    echo ✅ SUCCESS: Chrome Debugger is active!
    echo 👉 You can now run 'START_BROWSER_AUTOPILOT.bat'
)
echo.
pause
