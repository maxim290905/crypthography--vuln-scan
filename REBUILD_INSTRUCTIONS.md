# Инструкции по пересборке после исправлений

## Исправленные проблемы:

1. ✅ Добавлены системные зависимости для WeasyPrint (libpango, libcairo и др.)
2. ✅ Исправлена проблема с базой данных

## Шаги для пересборки:

### Вариант 1: Полная пересборка (рекомендуется)

```bash
# 1. Остановите контейнеры
sudo docker-compose down

# 2. Удалите старый том базы данных (если была проблема с именем базы)
sudo docker volume rm crypthography--vuln-scan_postgres_data

# 3. Пересоберите и запустите
sudo docker-compose up --build
```

### Вариант 2: Пересборка только API и Worker

```bash
# 1. Остановите контейнеры
sudo docker-compose down

# 2. Пересоберите только API и Worker
sudo docker-compose build --no-cache api worker

# 3. Запустите
sudo docker-compose up
```

### Вариант 3: Использование скрипта

```bash
./fix_database.sh
# Затем:
sudo docker-compose up --build
```

## Проверка после запуска:

1. **Проверьте логи API** - должно быть сообщение о создании admin пользователя:
```bash
sudo docker-compose logs api | grep -i "admin"
```

2. **Проверьте, что API запустился без ошибок**:
```bash
sudo docker-compose logs api | tail -20
```

3. **Проверьте доступность**:
   - API: http://localhost:8000/docs
   - Frontend: http://localhost:3000

4. **Попробуйте войти**: admin@example.com / admin123

## Если проблемы остались:

1. **Проверьте имя базы данных**:
```bash
sudo docker-compose exec postgres psql -U cryptscan -c "\l"
```

2. **Создайте базу вручную, если нужно**:
```bash
sudo docker-compose exec postgres psql -U cryptscan -c "CREATE DATABASE cryptscan_db;"
```

3. **Создайте admin пользователя вручную**:
```bash
sudo docker-compose exec api python -c "from app.startup import init_db; init_db()"
```

