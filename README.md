# Проект Фудграм.
## Описание проекта.
Проект представляет собой веб-приложение о еде и рецептах. Позволяет пользователям делиться рецептами.
Рецепты доступны без регистрации. Для возможности добавления своих рецептов, нужно зарегистрироваться.
С регистрацией доступны сервисы добавления рецептов и авторов в избранное, добавления рецептов в корзину, 
позволяющей сформировать список покупок для продуктов, необходимых для приготовления блюд.

### Проект в сети интернет.
Рабочий проект размещен по адресу: <https://fg.zapto.org/>

## Стек технологий.
* Язык програмирования, интерпретатор - Python 3.12.8
* Фронтенд — SPA-приложение - React Framework.
* Бекенд написан на Django 5.2.5
* API - Djanngo Rest Framework 3.16.
* Сериализация JSON
* Аутентификацция по токену - Djoser 2.3.3
* Проект размещен, используя контейнеризацию и оркестрирование - Docker 28.3.3
* Веб сервер - Nginx 1.25
* База данных - PostgreSQL 14
* Контроль версий - Git 2.48.1
* Файлы конфигураций - YAML
* Автоматизация CI/CD - workflow GitHub Actions
* Размещение на сервере под управлением Linux

## Установка интерпретатора Python.
 * Для Windows 10 и выше
Зайдите на страницу загрузки Python 3.12.7 на официальном сайте.

    <https://www.python.org/downloads/release/python-3127/>

 * Для Linux (Ubuntu)
    На Ubuntu интерпретатор Python уже предустановлен. Чтобы узнать его версию, введите команду:
    ```
    python3 --version
    ```
    
    Если нужно установить, то необходимо выполнить шаги:

    * Чтобы обновить пакеты системы — используйте пакетный менеджер apt. Введите в терминал команду:
    ```
    sudo apt update && sudo apt upgrade
    ```
    * Запустить установку нужной версии Python и пакетов для неё. Выполните последовательно команды:
    ```
    sudo apt install python3.12 
    ```    

## Локальный запуск проекта с Docker Compose:
1. Установить Docker в среду ОС:

    <https://docs.docker.com/get-started/get-docker/>


2. Клонирование репозитория.
   * Создать и перейти в папку проекта:
   ``` 
   mkdir foodgram
   ```
   ```
   cd foodgram
   ```
   * Находясь в папке проекта, выполнить команду:
   ```
   git clone git@github.com:mercure7/foodgram.git
   ```
3. Создать файл **.env**. Пример файла - **.env.example**

4. Находясь в корне проекта выполнить команду по сборке проекта из файла **docker-compose**. Данная команда соберет контейнеры, описанные в Docker файлах каждого приложения (frontend, backend, infra), контейнер с базой данных
и необходимые тома для хранения базы, статики и файлов медиа:

     Ниже приведены команды для ОС Linux. В среде Windows команды нужно выполнять без приставки *sudo*.
    ```
    sudo docker compose -f docker-compose.production.yml up -d
    ```
    Флаг **-d** собирает и запускает контейнеры в фоновом режиме.
5. Выполнить миграции внутри контейнера:
     ```
     sudo docker compose exec backend python manage.py migrate
     ```    
6. Создать суперпользователя:
    ```
    sudo docker compose exec backend python manage.py createsuperuser
    ```
7. Сборка статики и копирование статики в папку, объединенную volumes с веб-сервером:
    
    ```
    sudo docker compose exec backend python manage.py collectstatic
    ```
    ```
    sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/ 
    ```
8. * Наполнить базу данных примерами ингредиентов и тегов.

      - Импорт данных для таблицы Ingredients:
    ``` 
    sudo docker compose exec backend python manage.py ingredients_import_csv data/ingredients.csv 
    ```
    
      - Импорт данных для таблицы Tags:

    ```
    sudo docker compose exec backend python manage.py tags_import_csv data/tags.csv 
    ```    

9. Проверить работу проекта по адресу: 

    <http://127.0.0.0/>

10. Админ зона доступна по адресу:

    <http://127.0.0.0/admin/>

## Команды для работы с контейнерами (в случае необходимости перезапуска или выполнения новых команд):

* Остановка всех контейнеров:
    ```
    sudo docker compose stop
    ```
* Остановка и удаление всех контейнеров:
    ```
    sudo docker compose down
    ```
* Остановка и удаление всех контейнеров и volume (позволяет начать все сначала):
    ``` 
    docker compose down -v
    ```
* Команда для запуска  новой команды в запущенном контейнере:
    ```
    docker compose exec имя_контейнера команда
    ```
* Если файл называется не docker-compose.yml, то в каждой команде после compose нужно указывать параметр **-f имя_файла**, например:
    ```
    docker compose -f имя_файла up
    ```
* Команда сбора образа локально:
    ```
    docker build -t username_dockerhub/имя_образа .
    ```
* Отправка образа в облако DockerHub:
    ```
    docker push username_dockerhub/имя_образа 
    ```
* Подключение к удаленному серверу:
    ```
    ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
    ``` 

## Локальный запуск проекта без контейнеризации:

1. Запуск Frontend. Находясь в папке infra, выполните в терминале команду 
    ```
    docker compose up
    ```
    При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для фронтенд-приложения, а затем прекратит свою работу. 
    По адресу <http://127.0.0.0> будет доступен фронтенд веб-приложения, 
    а по адресу <http://127.0.0.0/api/docs/> — подробная спецификация API.
    
    Для правильной конфигурации веб-сервера нужно переименовать файл **nginx.conf.bak** в **nginx.conf** и сделать бекап существующего файла **nginx.conf**

2. Запуск backend. Клонирование репозитория.
   * Создать и перейти в папку проекта:
   ``` 
   mkdir foodgram
   ```
   ```
   cd foodgram
   ```
   * Находясь в папке проекта, выполнить команду:
   ```
   git clone git@github.com:mercure7/foodgram.git
   ```
3. Настроить виртуальное окружение:
    * OS Linux
    ```
    python3 -m venv venv
    ```
    * OS Windows
    ```
    python -m venv venv
    ```
4. Активировать виртуальное окружение:

    * Команда выполняется из директории с папкой venv.

      * Команда для Windows:
      ```
      source venv/Scripts/activate
      ```

      * Для Linux:
      ```
      source venv/bin/activate
      ```
5. Обновить пакетный менеджер **pip**:

    * Для Windows:
    ```
    python -m pip install --upgrade pip
    ```
    * Linux:
    ```
    python3 -m pip install --upgrade pip
    ```
6. Установить модули из файла requirementst.txt:
    ``` 
    pip install -r requirements.txt
    ```

7. Создать файл **.env**. Пример файла - **.env.example**

8. Выполнить миграции:
     ```
     python manage.py migrate
     ```    
9. Создать суперпользователя:
    ```
    python manage.py createsuperuser
    ```
10. Наполнить базу данных примерами ингредиентов и тегов.

      - Импорт данных для таблицы Ingredients:
    ``` 
    python manage.py ingredients_import_csv data/ingredients.csv 
    ```
    
      - Импорт данных для таблицы Tags:

    ```
    python manage.py tags_import_csv data/tags.csv 
    ```    
11. Запуск проекта:
    ```
    python manage.py runserver
    ```

12. Проверить работу проекта по адресу: 

    <http://127.0.0.0:8000/>

14. Админ зона доступна по адресу:

    <http://127.0.0.0:8000/admin/>

15. Интерфейс REST API Django доступен по адресу:
    <http://127.0.0.0:8000/api/>

#### Проект построен на базе данных postgres. Для запуска локально с базой данных SQLite необходми изменить настройки settings.py - DATABASES.

    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    ```

## CD/CI для развертывания

В папке .github/workflow/ расположен файл main.yml - worlkflow для автоматизации CI/CD в среде GitHub Actions. Необходимые переменные с секретными ключами и паролями необходимо предварительно сохранить в разделе настроек Actios -> Secrets.

Workflow настроен таким образом, что при срабатывании триггера *git push* из репозитория извелкается код, запускается процесс интегррования кода (CI) - тестирование кода на соответствие стандарту PEP8.

Далее происходит сборка образов фронтенд, бекенда и gateway сервера, отправка образов в DockerHub.

В случае успешного завершения CI происходит автоматический деплой на сервер, выполнение необходмых команд внутри контейнера для выполения миграций, сбора статики и запуска проекта (CD)

В случае успешного заверешения CI/CD автору приходит уведомление от Telegram Bot об успешном завершении операций.

## Примеры запросов, ответов API.

* Регистрация пользователя - POST:

     <http://127.0.0.1/api/users/>

     - Payload
        ```
        {
        "email": "test@test.ru",
        "username": "new_user",
        "first_name": "Имя",
        "last_name": "Фамилия",
        "password": "SecretPass"
         }
        ```
     - Примет ответа:
        ```
        {
        "email": "test@test.ru",
        "id": 0,
        "username": "new_user",
        "first_name": "Имя",
        "last_name": "Фамилия"
        }

        ```

* Получить список рецептов - GET:
    
    <http://127.0.0.1/api/recipes/>

     - Пример ответа:
     ```
    {
    "count": 123,
    "next": "http://foodgram.example.org/api/recipes/?page=4",
    "previous": "http://foodgram.example.org/api/recipes/?page=2",
    "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://foodgram.example.org/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
       }
      ]
    }
    ```
     
* Получить подписки пользователя - GET:

    <http://127.0.0.1/api/users/subscriptions/>
    - Пример ответа:
    ```
    {
  "count": 123,
  "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
  "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Иванов",
      "is_subscribed": true,
      "recipes": [
        {
          "id": 0,
          "name": "string",
          "image": "http://foodgram.example.org/media/recipes/images/image.png",
          "cooking_time": 1
        }
      ],
      "recipes_count": 0,
      "avatar": "http://foodgram.example.org/media/users/image.png"
       }
     ]
   }
    ```

### 





## Автор
Андрей Юркевич

GitHub:
<https://github.com/mercure7>

Email:
<a.jurkevich@gmail.com>
