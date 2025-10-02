# LCT Dashboard - Система анализа отзывов Газпромбанка

Веб-приложение для анализа клиентских отзывов с интерактивными графиками и метриками.

## 🚀 Быстрый старт

### Запуск с Docker (рекомендуется)

#### Продакшен версия
```bash
# Сборка и запуск продакшен версии
docker-compose up --build

# Или запуск в фоне
docker-compose up -d --build
```

Приложение будет доступно по адресу: http://localhost:3000

#### Версия для разработки
```bash
# Запуск dev версии с hot reload
docker-compose --profile dev up --build lct-dev
```

Приложение будет доступно по адресу: http://localhost:5173

### Локальный запуск

```bash
# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev

# Сборка для продакшена
npm run build

# Предпросмотр собранной версии
npm run preview
```

## 🐳 Docker команды

### Основные команды
```bash
# Сборка образа
docker build -t lct-dashboard .

# Запуск контейнера
docker run -p 3000:80 lct-dashboard

# Остановка всех контейнеров
docker-compose down

# Просмотр логов
docker-compose logs -f

# Пересборка без кэша
docker-compose build --no-cache
```

### Управление контейнерами
```bash
# Список запущенных контейнеров
docker ps

# Вход в контейнер
docker exec -it lct-dashboard sh

# Удаление неиспользуемых образов
docker image prune
```

## 📁 Структура проекта

```
LCT/
├── src/
│   ├── App.jsx          # Основной компонент приложения
│   └── App.css          # Стили приложения
├── public/              # Статические файлы
├── Dockerfile           # Конфигурация для продакшена
├── Dockerfile.dev       # Конфигурация для разработки
├── docker-compose.yml   # Оркестрация контейнеров
├── nginx.conf          # Конфигурация Nginx
└── .dockerignore       # Исключения для Docker
```

## 🛠️ Технологии

- **Frontend**: React 18, Vite
- **Графики**: Recharts
- **Стили**: CSS с BEM методологией
- **Контейнеризация**: Docker, Docker Compose
- **Веб-сервер**: Nginx (в продакшене)

## 📊 Функциональность

### Основные страницы
- **Главная** - Общая статистика и KPI
- **Кластеризация** - Анализ по категориям услуг
- **Тестирование** - Загрузка данных и метрики качества
- **Документация** - Руководство пользователя

### Возможности
- 📈 Интерактивные графики (линейные и круговые диаграммы)
- 🎛️ Фильтрация по категориям и временным периодам
- 📱 Адаптивный дизайн с мобильным меню
- 📄 Загрузка и скачивание JSON файлов
- 🔍 Детальная аналитика по метрикам

## 🔧 Переменные окружения

Создайте файл `.env` для настройки:

```env
# Порт для разработки
VITE_PORT=5173

# API endpoints (если нужны)
VITE_API_URL=http://localhost:8000

# Режим работы
NODE_ENV=development
```

## 📝 Разработка

### Добавление новых компонентов
1. Создайте компонент в `src/components/`
2. Добавьте стили в `src/App.css`
3. Импортируйте в `src/App.jsx`

### Обновление Docker образов
```bash
# Пересборка после изменений
docker-compose up --build

# Принудительная пересборка
docker-compose build --no-cache
```

## 🚀 Деплой

### Продакшен с Docker
```bash
# Сборка оптимизированного образа
docker build -t lct-dashboard:latest .

# Запуск в продакшене
docker run -d -p 80:80 --name lct-prod lct-dashboard:latest
```

### CI/CD пример
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker image
        run: |
          docker build -t lct-dashboard .
          docker run -d -p 3000:80 lct-dashboard
```

## 🐛 Устранение неполадок

### Проблемы с Docker
```bash
# Очистка Docker кэша
docker system prune -a

# Перезапуск Docker daemon
sudo systemctl restart docker

# Проверка логов контейнера
docker logs lct-dashboard
```

### Проблемы с портами
```bash
# Проверка занятых портов
netstat -tulpn | grep :3000

# Изменение порта в docker-compose.yml
ports:
  - "8080:80"  # Используйте другой порт
```

## 📞 Поддержка

- **Email**: analytics@gazprombank.ru
- **Техподдержка**: +7 (495) 123-45-67
- **Версия**: 1.0.0

## 📄 Лицензия

Внутренний проект Газпромбанка. Все права защищены.