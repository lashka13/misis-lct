@echo off
echo ===== Проверка Docker =====
docker --version
if %errorlevel% neq 0 (
    echo Docker не установлен!
    pause
    exit /b 1
)

echo.
echo ===== Проверка Docker Compose =====
docker compose version
if %errorlevel% neq 0 (
    echo Docker Compose не доступен!
    pause
    exit /b 1
)

echo.
echo ===== Сборка и запуск контейнера =====
docker compose up --build -d

echo.
echo ===== Проверка запущенных контейнеров =====
docker ps

echo.
echo ===== Проверка логов =====
docker compose logs --tail=20

echo.
echo ===== Проверка доступности приложения =====
timeout /t 5 /nobreak > nul
curl -I http://localhost:3000 2>nul
if %errorlevel% equ 0 (
    echo ✅ Приложение доступно на http://localhost:3000
) else (
    echo ❌ Приложение недоступно
)

echo.
echo Нажмите любую клавишу для завершения...
pause > nul

