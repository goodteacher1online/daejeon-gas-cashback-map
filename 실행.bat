@echo off
chcp 65001 > nul
title 온통대전 주유소 실시간 지도 (GitHub 최신)
echo ========================================================
echo   [온통대전 실시간 지도] 최신 유가 자동 확인 및 실행 중...
echo ========================================================
echo.
python "%~dp0update_prices.py"
echo.
echo 브라우저로 지도를 실행합니다...
start "" "%~dp0index.html"