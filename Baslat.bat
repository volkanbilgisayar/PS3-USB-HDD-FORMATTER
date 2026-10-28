@echo off
chcp 65001 >nul
title FAT32 Pro Formatter (PS3 & USB 500GB+)

:: Yönetici Olarak Çalıştır (UAC İzni İste)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [BİLGİ] Yönetici izni isteniyor...
    powershell -ExecutionPolicy Bypass -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

if exist "FAT32_Pro_Format.exe" (
    start "" "FAT32_Pro_Format.exe"
    exit /b
)

if exist "fat32_formatter.py" (
    start "" py "fat32_formatter.py"
    exit /b
)

echo [HATA] FAT32_Pro_Format.exe veya fat32_formatter.py bulunamadı!
pause
