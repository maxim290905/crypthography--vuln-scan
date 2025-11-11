# Cryptography Vulnerability Scanner - MVP

Автоматизированный инструмент для сканирования TLS/сертификатов и сетевой поверхности с генерацией отчетов и PQ-score.

## Архитектура

- **Frontend**: React приложение для управления сканами
- **Backend**: FastAPI REST API
- **Worker**: Celery worker для выполнения сканирований
- **Database**: PostgreSQL для хранения результатов
- **Queue**: Redis для очереди задач
- **Tools**: testssl.sh, nmap и PQC Scanner для сканирования

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

## Инструменты сканирования

### PQC Scanner (Post-Quantum Cryptography Scanner)

**PQC Scanner** — это встроенный Python-модуль для определения поддержки Post-Quantum Cryptography алгоритмов на TLS-серверах. Это порт популярного Rust-сканера `pqcscan`.

#### Что делает PQC Scanner

PQC Scanner проверяет, поддерживает ли целевой TLS-сервер постквантовые криптографические алгоритмы, такие как:
- **MLKEM** (Module-Lattice-Based Key-Encapsulation Mechanism) — чисто PQC алгоритмы
- **Hybrid алгоритмы** — комбинации классических и PQC алгоритмов (например, X25519MLKEM768)

#### Как работает PQC Scanner

1. **Создание TLS ClientHello вручную**
   - Сканер создает TLS 1.3 ClientHello сообщения на низком уровне (бинарный протокол)
   - Включает расширения: Server Name Indication, Supported Versions, Supported Groups, Signature Algorithms, Key Share

2. **Тестирование PQC групп**
   - Для каждой PQC группы из конфигурации (`tls_groups.json`) сканер:
     - Создает TCP соединение с целевым сервером
     - Отправляет ClientHello с указанием конкретной PQC группы в `supported_groups` extension
     - Отправляет пустой `key_share` extension (сервер ответит своим выбором)

3. **Анализ ответа сервера**
   - **ServerHello (0x16)**: Если сервер отвечает ServerHello, это означает, что он поддерживает запрошенную PQC группу
   - **Alert (0x15)**: Если сервер отвечает Alert, это означает, что он не поддерживает запрошенную группу
   - Парсинг расширений ServerHello для определения выбранной группы и списка поддерживаемых групп

4. **Определение поддержки PQC**
   - Если получен ServerHello → группа поддерживается (даже если сервер выбрал другую группу)
   - Если сервер выбрал PQC группу → система определенно поддерживает PQC
   - Если запрошенная группа есть в `supported_groups` списке → группа поддерживается

#### Поддерживаемые PQC алгоритмы

Сканер тестирует следующие типы алгоритмов:

- **Чистые PQC алгоритмы:**
  - MLKEM512, MLKEM768, MLKEM1024
  - MLKEMED25519, ED25519MLKEM768

- **Hybrid алгоритмы (рекомендуются):**
  - X25519MLKEM768 (X25519 + MLKEM768)
  - SECP256R1MLKEM768 (SECP256R1 + MLKEM768)
  - SECP384R1MLKEM1024 (SECP384R1 + MLKEM1024)

#### Приоритет тестирования

Сканер тестирует группы в следующем порядке приоритета:
1. MLKEM768, MLKEM1024
2. X25519MLKEM768, SECP256R1MLKEM768
3. MLKEM512, MLKEMED25519, ED25519MLKEM768
4. Остальные PQC группы

#### Результаты сканирования

PQC Scanner возвращает:
- `pqc_supported`: `true`/`false` — поддерживает ли сервер PQC
- `pqc_algos`: список чистых PQC алгоритмов (например, ["MLKEM768"])
- `hybrid_algos`: список hybrid алгоритмов (например, ["X25519MLKEM768"])
- `nonpqc_algos`: список не-PQC алгоритмов (если тестируются)

#### Интеграция в общий сканер

PQC Scanner автоматически вызывается во время TLS/Network сканирования и результаты включаются в общий отчет. Если сервер не поддерживает PQC, создается finding с категорией `no_pqc_support` и приоритетом P0, что значительно снижает PQ-Score.

#### Пример использования

```python
from app.pqc_scanner import PQCScanner

scanner = PQCScanner()
result = scanner.scan_target("example.com", 443)

print(f"PQC Supported: {result['pqc_supported']}")
print(f"Hybrid Algos: {result['hybrid_algos']}")
print(f"PQC Algos: {result['pqc_algos']}")
```

### testssl.sh

Используется для глубокого анализа TLS/SSL конфигурации:
- Проверка поддерживаемых версий TLS
- Анализ cipher suites
- Проверка сертификатов
- Обнаружение уязвимостей (BEAST, POODLE, Heartbleed и др.)

### nmap

Используется для сетевого сканирования:
- Определение открытых портов
- Обнаружение TLS/SSL сервисов
- Анализ SSL/TLS конфигурации через NSE скрипты

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

PQ-score (Post-Quantum Security Score) — это комплексная оценка криптографической безопасности целевого хоста с учетом готовности к переходу на постквантовую криптографию.

### Как рассчитывается PQ-Score

PQ-score рассчитывается на основе следующих компонентов с весами:

- **No PQC Support** (30%): Отсутствие поддержки Post-Quantum Cryptography алгоритмов
- **Deprecated algorithms** (25%): Наличие устаревших алгоритмов (RSA<2048, MD5, SHA1)
- **Weak key sizes** (20%): Слабые размеры ключей (RSA < 3072, малые EC кривые)
- **Public exposure** (10%): Доступность из интернета
- **Cert lifecycle** (10%): Проблемы с сертификатами (истекшие/скоро истекающие)
- **Vulnerable dependencies** (5%): Уязвимые зависимости (если SBOM присутствует)

### Интерпретация PQ-Score

PQ-score — это значение от **0 до 100**, где:
- **100** — идеальный результат (нет проблем, PQC поддерживается)
- **0** — критическое состояние (множество серьезных уязвимостей, нет PQC)

#### Уровни риска:

| Диапазон | Уровень | Интерпретация | Рекомендации |
|----------|---------|---------------|--------------|
| **80-100** | **Low** | Низкий риск. Система в хорошем состоянии, PQC поддерживается или отсутствуют критические проблемы. | Продолжайте мониторинг, поддерживайте текущий уровень безопасности. |
| **60-79** | **Medium** | Средний риск. Есть проблемы, требующие внимания, но не критичные. Возможно отсутствие PQC поддержки. | Планируйте исправления в ближайшее время, рассмотрите внедрение PQC. |
| **40-59** | **High** | Высокий риск. Обнаружены серьезные проблемы безопасности, включая устаревшие алгоритмы или отсутствие PQC. | Требуется немедленное планирование исправлений. Приоритет на устранение критических уязвимостей. |
| **0-39** | **Critical** | Критический риск. Множество серьезных уязвимостей, отсутствие PQC, использование небезопасных алгоритмов. | **Немедленные действия обязательны.** Требуется срочное устранение всех критических проблем. |

### Что влияет на снижение PQ-Score

1. **Отсутствие PQC поддержки** (-30 баллов) — самый критичный фактор
   - Система не готова к переходу на постквантовую криптографию
   - Рекомендуется внедрение hybrid PQC алгоритмов (например, X25519MLKEM768)

2. **Устаревшие алгоритмы** (-25 баллов)
   - Использование MD5, SHA1, слабых версий TLS
   - Требуется обновление до современных стандартов

3. **Слабые ключи** (-20 баллов)
   - RSA ключи < 3072 бит
   - Малые EC кривые
   - Рекомендуется переход на более сильные ключи

4. **Публичная доступность** (-10 баллов)
   - Система доступна из интернета без дополнительной защиты
   - Рекомендуется применение дополнительных мер безопасности

5. **Проблемы с сертификатами** (-10 баллов)
   - Истекшие или скоро истекающие сертификаты
   - Неправильная конфигурация цепочки сертификатов

6. **Уязвимые зависимости** (-5 баллов)
   - Обнаружены известные уязвимости в зависимостях
   - Требуется обновление библиотек

### Как улучшить PQ-Score

1. **Внедрить PQC поддержку** — самый эффективный способ повысить оценку
2. **Обновить устаревшие алгоритмы** — заменить MD5/SHA1 на SHA-256/SHA-384
3. **Усилить ключи** — использовать RSA ≥ 3072 бит или современные EC кривые
4. **Исправить проблемы с сертификатами** — обновить истекающие сертификаты
5. **Обновить зависимости** — устранить уязвимости в используемых библиотеках

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

