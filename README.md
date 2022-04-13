[![foodgram CI/CD workflow](https://github.com/aafedotov/foodgram-project-react/actions/workflows/foodgram_cicd.yml/badge.svg?branch=master&event=deployment_status)](https://github.com/aafedotov/foodgram-project-react/actions/workflows/foodgram_cicd.yml)


https://aafedotov-foodgram.myddns.me/  
https://aafedotov-foodgram.myddns.me/admin/

В папке data размещены тестовые данные в csv для импорта в БД.  
(данные уже импортированы)

Учетные данные superuser для ревьювера:  
user: faa@faa.ru 
password: 123

## Учебный проект "Продуктовый Помощник"
### Автор: Андрей Федотов
### Cтудент когорты №5 pythonplus Яндекс.Практикум.

На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации 
других пользователей, добавлять понравившиеся рецепты в список «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления 
одного или нескольких выбранных блюд.

Для репозитория настроен CI/CD.
Для запуска приложения:

1. Сделайте Fork данного репозитория
2. Подготовьте vps с ubuntu и docker
3. Добавьте action secrets под Ваш проект:

DB_ENGINE  
DB_HOST  
DB_NAME  
DB_PORT  
DOCKER_PASSWORD  
DOCKER_USERNAME  
HOST  
PASSPHRASE  
POSTGRES_DB  
POSTGRES_PASSWORD  
POSTGRES_USER  
SECRET_KEY  
SSH_KEY  
TELEGRAM_TO  
(кому отправить сообщение о статусе ci/cd workflow)  
TELEGRAM_TOKEN  
(токен вашего телеграм бота)  
USER  
(пользователь на хосте)
