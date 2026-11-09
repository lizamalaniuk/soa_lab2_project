# ЛР2 SOA — варіант 11

Сервіси: users, homework, notifications; окремий RabbitMQ consumer, API Gateway (Nginx), Redis.

## Запуск
```bash
docker compose up --build -d
docker compose ps
curl http://localhost:8080/health
```

RabbitMQ UI: http://localhost:15672 (guest / guest).

## Послідовна перевірка

1. Створити учня:
```bash
curl -s -X POST http://localhost:8080/api/users -H 'Content-Type: application/json' -d '{"name":"Олена","email":"olena@example.com"}'
```
Скопіювати `id` з відповіді.

2. Створити завдання (замінити USER_ID):
```bash
curl -s -X POST http://localhost:8080/api/homeworks -H 'Content-Type: application/json' -d '{"user_id":"USER_ID","subject":"Математика","description":"Вправи 5–8","deadline":"2026-11-02"}'
```
Скопіювати `id` завдання. Поля `sync_user_checked` і `event_published` підтверджують успішне виконання обох операцій.

3. Перевірити події та повідомлення:
```bash
docker compose logs --tail=30 consumer
curl -s http://localhost:8080/api/notifications
```

4. Позначити виконаним (замінити TASK_ID):
```bash
curl -s -X PATCH http://localhost:8080/api/homeworks/TASK_ID/complete
curl -s http://localhost:8080/api/notifications
```

5. Горизонтальне масштабування і перевірка:
```bash
docker compose up -d --scale homework=3
docker compose ps
for i in {1..12}; do curl -s http://localhost:8080/api/homeworks; echo; done
```
У відповідях спостерігати поле `served_by` — ID контейнера, який обробив запит. Docker DNS відповідає за пошук інстансів; Nginx використовує його для маршрутизації. Вивід може залежати від кешування DNS та балансування.

## Завершення
```bash
docker compose down
```
