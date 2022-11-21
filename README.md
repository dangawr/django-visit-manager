## General Information
Simple Visit Manager with sms reminder. This app allows to add new clients and visits, filter clients and visits or
send sms to remind about visit. Application uses an external api to send sms messages - https://callapi.pl/docs/
App uses Postgres as database. Redis is used as Celery message broker/backend. 

## Technologies Used
- Django - version 4.0
- Celery
- Docker
- Redis
- Postgres

## To Do:
- Unit tests
- Deployment

## How to run:
- You must have installed docker. Then:
```
docker-compose up
```

![img.png](img/img.png)
![img_1.png](img/img_1.png)


