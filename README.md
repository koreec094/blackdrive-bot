# Telegram бот расчета авто (Казахстан)

## Возможности
- Пошаговый выбор: Марка → Модель → Год → Объем.
- Данные из Google Sheets (лист `База авто`).
- Запись входных данных в расчетный лист `Казахстан/Алматы` и чтение результата формул.
- История расчетов в `История расчетов`.
- Заявки на ручной расчет в `Заявки` + уведомление админов.
- Админ-команды: `/status`, `/reload`, `/stats`.

## Как создать Telegram-бота
1. Откройте BotFather.
2. Выполните `/newbot`.
3. Скопируйте токен в `BOT_TOKEN`.

## Как подключить Google Sheets API
1. В Google Cloud создайте проект.
2. Включите Google Sheets API.
3. Создайте Service Account.
4. Скачайте JSON-ключ и сохраните в `credentials/service-account.json`.
5. Дайте email service account доступ (Editor) к вашей таблице Google Sheets.

## Настройка `.env`
1. Скопируйте `.env.example` в `.env`.
2. Заполните обязательные поля.
3. `ADMIN_IDS` задается как CSV список Telegram ID.

## Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m bot.main
```

## Обновление базы авто
- Автоматически при старте.
- Вручную админ-командой `/reload`.

## Админ-команды
- `/status` — состояние бота.
- `/reload` — принудительное обновление кэша `База авто`.
- `/stats` — размер текущего кэша.
