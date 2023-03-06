Foodgram
---


### Статус workflow
[![foodgram_workflow](https://github.com/NikAfraim/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master)](https://github.com/NikAfraim/foodgram-project-react/actions/workflows/foodgram_workflow.yml)
---

### Описание

##### Идея проекта
Создать приложение «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


##### Задача проекта
Написать бэкенд проекта и **API** для него (приложение **api**)

Настроить для приложения Continuous Integration и Continuous Deployment.


### Технологии:
- Django 
- Django REST Framework
- Django Filter
- PyJWT
- Docker
- Docker-compose
- Nginx
- Gunicorn
- PostgreSQL
- DockerHub
- Yandex.Cloud
---
### Установка
##### Требования для корректной работы
[python 3.11](https://www.python.org/downloads/), django 3.2
##### Для тестирования запросов можно использовать
[Postman](https://www.postman.com/downloads/)
### Запуск проекта локально
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:NikAfraim/foodgram-project-react.git
```
```
cd foodgram-project-react
```
```
cd infra
```
---
Cоздать файл .env с внутренностями:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DEBUG=False
DATABASE=True
```
Создать образ и собрать контейнеры:
```
docker-compose up -d --build
```
Выполнить следующие команды по очереди(В случае использование ОС Windows, у второй и третий команты понадобится префикс "winpty"):
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
---

### Когда вы запустите проект, по адресу http://localhost/api/docs/ будет доступна документация проекта YaMDb.
---
Разработчик foodgram-project:
- Сенгилейцев Никита
