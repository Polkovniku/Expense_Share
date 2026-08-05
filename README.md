# Expense Share

REST API для врахування спільних витрат у групі. Додаток дозволяє фіксувати витрати учасників групи та автоматично розраховує, хто кому і скільки винен, мінімізуючи кількість переказів.

## Технології

- **Python 3.12** / **FastAPI** — основний фреймворк
- **SQLAlchemy 2.0 (async)** — ORM з асинхронними запитами
- **PostgreSQL 16** — база даних
- **Alembic** — міграції
- **Pydantic v2** — валідація даних
- **JWT (PyJWT)** — аутентифікація
- **pwdlib** — хешування паролів
- **Docker / Docker Compose** — контейнеризація

## Функціональність

- Реєстрація та аутентифікація користувачів (JWT access + refresh токени)
- створення груп для спільних витрат (поїздка, оренда і т.д.)
- Додавання учасників до групи 
- Фіксація витрат із гнучким розподілом: на всіх учасників порівну або на конкретний список учасників
- Облік погашень боргів (Settlement)
- Розрахунок чистого балансу кожного учасника
- **Алгоритм мінімізації переказів** — система автоматично розраховує мінімальний набір переказів, що закривають усі борги

## Алгоритм спрощення боргів

Замість того щоб рахувати борги по кожній транзакції окремо (що може давати надлишкові ланцюжки), система:

1. Рахує **чистий баланс** кожного учасника за формулою:
```
баланс = (сума оплачених витрат) − (сума своїх часток) + (отримані погашення) − (відправлені погашення)
```

2. Застосовує **жадібний алгоритм**:
   - Учасники поділяються на кредиторів (баланс > 0) та боржників (баланс < 0) 
   - На кожному кроці береться боржник із максимальним боргом і кредитор із максимальною вимогою 
   - Між ними фіксується переказ у сумі `min(|долг|, вимога)` 
   - Хоча б один із двох повністю закриває свій баланс на кожному кроці 
   - Алгоритм завершується, коли всі баланси дорівнюють нулю

## Структура проекту

```
app/
├── core/
│   ├── config.py          # налаштування (pydantic-settings)
│   ├── database.py        # підключення бд та сесія
│   ├── dependencies.py    # get_db, get_current_user
│   └── security.py        # хешування паролів, JWT токени
├── users/
│   ├── models.py
│   ├── schemas.py
│   ├── service.py         # реєстрація, логін, оновлення токена
│   └── router.py
├── groups/
│   ├── models.py          # Group, GroupMember
│   ├── schemas.py
│   ├── service.py         # GroupService, GroupMemberService
│   └── router.py
├── expenses/
│   ├── models.py          # Expense, ExpenseShare
│   ├── schemas.py
│   ├── service.py         # створення витрат з автоматичним розподілом часток
│   └── router.py
├── settlements/
│   ├── models.py
│   ├── schemas.py
│   ├── service.py
│   └── router.py
├── balances/
│   ├── schemas.py
│   ├── service.py         # calculate_balance, simplify_debts
│   └── router.py
└── main.py
```

## База даних

Шість таблиць:

- `users` - зареєстровані облікові записи
- `groups` - групи (поїздки, події)
- `group_members` - учасники групи (може бути без облікового запису - "привид")
- `expenses` - витрати (хто заплатив і скільки)
- `expense_shares` - частки кожного учасника в конкретній витрати
- `settlements` - факти погашення боргів

Усі витрати та розрахунки посилаються на `GroupMember`, а не безпосередньо на `User` - це дозволяє враховувати учасників без облікового запису нарівні із зареєстрованими користувачами.

## API ендпоінти

### Auth / Users
| Метод | Шлях | Опис |
|-------|------|----------|
| POST | `/auth/register` | Реєстрація |
| POST | `/auth/login` | Логін, отримання токенів |
| POST | `/auth/token` | Оновлення access токена |
| GET | `/auth/me` | Дані поточного користувача |

### Groups
| Метод | Шлях | Опис |
|-------|------|----------|
| POST | `/groups/` | Створити групу |
| GET | `/groups/{group_id}` | Отримати групу |
| PATCH | `/groups/{group_id}` | Оновити групу |
| DELETE | `/groups/{group_id}` | Видалити групу |
| GET | `/groups/{group_id}/members` | Учасники групи |
| POST | `/groups/{group_id}/members` | Додати учасника |

### Expenses
| Метод | Шлях | Опис |
|-------|------|----------|
| GET | `/groups/{group_id}/expenses/` | Список витрат групи |
| POST | `/groups/{group_id}/expenses/` | Створити витрату |
| GET | `/groups/{group_id}/expenses/{expense_id}` | Отримати витрату |
| GET | `/groups/{group_id}/expenses/{expense_id}/shares` | Частки з витрати |

### Settlements
| Метод | Шлях | Опис |
|-------|------|----------|
| GET | `/groups/{group_id}/settlements/` | Історія погашень |
| POST | `/groups/{group_id}/settlements/` | Зафіксувати погашення |

### Balances
| Метод | Шлях | Опис |
|-------|------|----------|
| GET | `/groups/{group_id}/balances/` | Сирі баланси учасників |
| GET | `/groups/{group_id}/balances/simplified` | Мінімальний набір переказів |

## Запуск

1. Клонувати репозиторій:
```bash
git clone https://github.com/Polkovniku/Expense_Share.git
cd expense-share
```

2. Створити `.env` файл:
```env
POSTGRES_DB=expense_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
DB_HOST=expense-db
DB_PORT=5432
SECRET_KEY=your_secret_key
```

3. Запустити через Docker Compose:
```bash
docker-compose up --build
```

4. Відкрий документацію API:
```
http://localhost:8000/docs
```

5. Зупинити сервіси

```
docker compose down
```


## Генерація SECRET_KEY

```bash
openssl rand -hex 32
```


