## General Information
Visit Manager with SMS reminder. This app allows to add new clients, their visits, 
check free dates and filter clients in database. To remind the customer about the visit,
the application searches for customers with upcoming visits every day using 'Celery'
and sends them SMS reminder. Application uses an external api to send sms messages - https://callapi.pl/docs/
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


