# Проект Фудграм.
Проект о еде и рецептах. Позволяет пользователям делиться рецептами. 

## Особенности проекта
* Frontend построен на React
* Backend построен на Rest API

## Проект в сети интернет.
Рабочий проект размещен по адресу: https://fg.zapto.org/.
Рецепты доступны беслатно. Для возможности добавдения своих, нужно зарегистрироваться.

## Запуск на локальном сервере.
### Как запустить frontend:
* Для запуска проекта в системе должен быть установлен Docker.
```
https://docs.docker.com/get-started/get-docker/
```

* Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:mercure7/foodgram.git
```

```
cd foodgram
```
Проект построен на базе данных postgres. Для запуска локально с базой данных SQLite необходми изменить настройки settings.py - DATABASES.

Находясь в папке foodgram, выполните команду docker-compose up. 
При выполнении этой команды docker соберет контейнеры описанные в docker-compose.yml, подготовит файлы, необходимые для запуска проекта.
Проект будет доступен по адресу:

http://127.0.0.1/


* Зайти в созданную сеть докер, выполнить миграции.

```
docker compose exec backend python manage.py migrate 

```
* Наполнить базу данных примерами ингредиентов и тегов.

 - Импорт данных для таблицы Ingredients:
``` python manage.py ingredients_import_csv foodgram_backend/data/ingredients.csv ```
``` python manage.py tags_import_csv foodgram_backend/data/tags.csv ```

## REST API
Frontend и backend проекта взаимодейсивуют по API.
Полную документацию, примеры запросов и ответов можно найти в файле /data/openapi-schema.yml

### Авторы
* Yandex Practicum - frontend
* Andrei Yurkevich @mercure7 a.jurkevich@gmail.com - backend
