# MA Family Budget

Приложение для семейного бюджета с телеграм-ботом.

## Быстрый запуск

1. Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Отредактируйте `.env` файл, указав ваш токен телеграм-бота:
```bash
BOT_TOKEN=your_actual_bot_token_here
```

3. Запустите приложение:
```bash
docker compose up -d
```

## Остановка

```bash
docker compose down
```

## Логи

```bash
docker compose logs -f
```
