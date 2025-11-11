# Исправления проблем

## Проблемы, которые были исправлены:

1. ✅ Добавлен `email-validator` в requirements.txt (нужен для Pydantic EmailStr)
2. ✅ Исправлен startup event для правильной инициализации БД
3. ✅ Удален устаревший атрибут `version` из docker-compose.yml

## Что нужно сделать:

1. **Остановите текущие контейнеры** (если запущены):
```bash
sudo docker-compose down
```

2. **Пересоберите контейнеры с исправлениями**:
```bash
sudo docker-compose build --no-cache api worker
```

3. **Запустите заново**:
```bash
sudo docker-compose up
```

4. **Проверьте логи API**, чтобы убедиться, что пользователь создан:
```bash
sudo docker-compose logs api | grep -i "admin"
```

Должно появиться сообщение: `✓ Admin user created: admin@example.com / admin123`

5. **Если пользователь не создался**, создайте его вручную:
```bash
sudo docker-compose exec api python -c "from app.startup import init_db; init_db()"
```

## Проверка работы:

После запуска проверьте:
- API доступен: http://localhost:8000/docs
- Frontend доступен: http://localhost:3000
- Попробуйте войти: admin@example.com / admin123

