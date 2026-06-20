FROM node:22-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173
# хост 0.0.0.0, чтобы Vite был доступен снаружи контейнера
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
