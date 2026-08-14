@echo off
REM Wrapper tien loi cho update.ps1 (double-click duoc tren Windows).
REM Toan bo logic that nam trong update.ps1 - file nay CHI goi no, khong
REM lap lai code, tranh 2 noi phai sua khi co thay doi.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update.ps1"
pause
