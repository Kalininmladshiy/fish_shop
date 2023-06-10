# fish_shop
Данный репозиторий представляет собой MVP телеграм бота магазина на базе CMS [Elasticpath](https://www.elasticpath.com/).

## Установка:

### 1. Копируем содержимое проекта себе в рабочую директорию

### 2. Для хранения переменных окружения создаем файл .env:
```
touch .env
```
В проекте используются следующие переменные окружения:  
`TG_BOT_TOKEN` - Телеграм токен. Его вы получите при регистрации бота  
`ACCESS_TOKEN` - Токен CMS системы. Как его получить можно почитать по [ссылке](https://elasticpath.dev/docs/commerce-cloud/api-overview/your-first-api-request)  
`PRICE_BOOK_ID` - ID вашего прайс-листа. Его вы можете найти в меню CMS  
`ALLOWED_HOSTS` - Хост для Redis  
`DECODE_RESPONSES` - Установите значение True для Redis, если вы хотите получать декодированные строки, а не байты  
`PORT` - Порт для Redis  
`DB` -  Номер базы данных в Redis к которой вы хотите подключиться (по умолчанию 0)  

### 3. Разворачиваем внутри скопированного проекта виртуальное окружение:
```
python -m venv <название виртуального окружения>
```
```
source venv/bin/activate
```
### 4. Устанавливаем библиотеки:
```
pip install -r requirements.txt
```

### 5. Запускаем бота магазина в телеграм:
```
python fish_shop.py
```

## Возможные ошибки при запуске.  
Проект использует технологию Redis для кэширования вопросов, поэтому при первом запуске вы можете 
столкнуться со следующе ошибкой `ConnectionRefusedError: [Errno 111] Connection refused`.  
Для ее решения проверьте подключение к Redis
```
redis-cli ping
```
Возможно для выполнения этой команды вас попросят выполнить следущую команду:
```
apt install redis-tools
```
Если после выполнения `redis-cli ping` вы получили ошибку `Could not connect to Redis at 127.0.0.1:6379: Connection refused`, выполните
следующую команду:
```
redis-server
```
Возможно для выполнения этой команды вас попросят выполнить следущую команду:
```
apt install redis-server
```
После этого перезапустите бота.

Про ошибки запросов к CMS системе можно почитать [здесь](https://elasticpath.dev/docs/commerce-cloud/api-overview/errors)

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org/).
