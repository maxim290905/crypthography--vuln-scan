# Cryptography Vulnerability Scanner - MVP

Автоматизированный инструмент для сканирования TLS/сертификатов и сетевой поверхности с генерацией отчетов и PQ-score.

## Архитектура

- **Frontend**: React приложение для управления сканами
- **Backend**: FastAPI REST API
- **Worker**: Celery worker для выполнения сканирований
- **Database**: PostgreSQL для хранения результатов
- **Queue**: Redis для очереди задач
- **Tools**: testssl.sh и nmap для сканирования

## Быстрый старт

### Требования

- Docker и Docker Compose
- Git

### Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd crypthography--vuln-scan
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Запустите все сервисы:
```bash
docker-compose up --build
```

4. Приложение будет доступно:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Nginx (reverse proxy): http://localhost:80

### Первоначальная настройка

При первом запуске автоматически создается административный пользователь:
- **Email**: admin@example.com
- **Password**: admin123

Вы можете войти в систему через веб-интерфейс или создать дополнительных пользователей через API:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "User Name",
    "role": "user"
  }'
```

## API Документация

После запуска API документация доступна по адресу: http://localhost:8000/docs

### Основные endpoints:

- `POST /api/auth/login` - Аутентификация
- `POST /api/scans` - Создать задание на сканирование
- `GET /api/scans/{scan_id}/status` - Статус скана
- `GET /api/scans/{scan_id}/result` - Результаты скана (JSON)
- `GET /api/scans/{scan_id}/report.pdf` - Скачать PDF отчет
- `GET /api/assets` - Список просканированных assets

## Использование

### Создание скана через API

```bash
# 1. Войдите в систему
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}' \
  | jq -r '.access_token')

# 2. Создайте проект (если нужно)
PROJECT_ID=$(curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project"}' \
  | jq -r '.id')

# 3. Создайте скан
SCAN_ID=$(curl -X POST http://localhost:8000/api/scans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "example.com",
    "project_id": '$PROJECT_ID',
    "scan_type": "tls_network"
  }' \
  | jq -r '.id')

# 4. Проверьте статус
curl -X GET http://localhost:8000/api/scans/$SCAN_ID/status \
  -H "Authorization: Bearer $TOKEN"

# 5. Получите результаты
curl -X GET http://localhost:8000/api/scans/$SCAN_ID/result \
  -H "Authorization: Bearer $TOKEN"

# 6. Скачайте PDF отчет
curl -X GET http://localhost:8000/api/scans/$SCAN_ID/report.pdf \
  -H "Authorization: Bearer $TOKEN" \
  -o report.pdf
```

## Структура проекта

```
.
├── backend/          # FastAPI приложение и Celery worker
├── frontend/         # React приложение
├── nginx/            # Nginx конфигурация
├── storage/          # Хранилище отчетов (PDF, JSON)
├── docker-compose.yml
└── README.md
```

## PQ-Score алгоритм

PQ-score рассчитывается на основе следующих компонентов:

- **Deprecated algorithms** (35%): Наличие устаревших алгоритмов (RSA<2048, MD5, SHA1)
- **Weak key sizes** (25%): Слабые размеры ключей (RSA < 3072, малые EC кривые)
- **Public exposure** (20%): Доступность из интернета
- **Cert lifecycle** (10%): Проблемы с сертификатами (истекшие/скоро истекающие)
- **Vulnerable dependencies** (10%): Уязвимые зависимости (если SBOM присутствует)

**Thresholds:**
- 0-30: Low
- 31-60: Medium
- 61-85: High
- 86-100: Critical (P0)

## Безопасность

- Все сканирования выполняются в изолированном контейнере с ограничениями ресурсов
- Валидация входных данных (targets)
- JWT аутентификация с коротким сроком жизни токенов
- Пароли хранятся с использованием bcrypt
- Аудит логи всех действий

## Разработка

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Тесты

```bash
cd backend
pytest
```

## Лицензия

[Укажите лицензию]

