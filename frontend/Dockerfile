# Используем официальный образ Node.js как базовый
FROM node:18-alpine as build

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm ci

# Копируем исходный код приложения
COPY . .

# Собираем приложение для продакшена
RUN npm run build

# Используем nginx для раздачи статических файлов
FROM nginx:alpine

# Копируем собранное приложение в nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx для SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]
