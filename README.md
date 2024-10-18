# Django project with Swagger Documentation
## Description:
A simple Django application that implements a CRUD API (Create, Read, Update, and Delete) for managing a weekly schedule with IDs associated with time slots for each day of the week. The application includes Swagger documentation and logic of a basic authentication via JWT Tokens.

## Technologies:
In project technologies are used:
- Django (Django Rest Framework);
- PostgreSQL;
- Pytest;
- Swagger Documentation;
- Docker;

## Build and Run:
First, you need to clone the project from GitHub repository:
```
git clone https://github.com/Serhii-Voloshyn/managing-weekly-schedule.git
```
After cloning the project, you need a build project via Docker. In your project terminal, write this command for building.
```
docker-compose up --build
```
Now you need a make migrations for declaring table in DB. Run this command in the second parallel terminal.
```
docker-compose exec web python manage.py makemigrations
```
And then this.
```
docker-compose exec web python manage.py migrate
```
Also for testing APIs and JWT, you need to register user. Just for testing, you can use superuser. 
Register superuser via terminal (of course, the project must be active. You can register superuser in the second terminal):
```
docker-compose run web python manage.py createsuperuser 
```

## Test via Pytest
If you want to test APIs in a project via pytest, you need a run following command in the second terminal while a project is running.
```
docker-compose exec web pytest -v
```

## Manual Testing
You can test the APIs of this project via Postman or Swagger. 

The first option, you need a Postman where you create requests with api references and a jwt token in the header.

The second option, it's via Swagger in browser. After running the project, follow the link to test `/swagger/`.

#### Warning!
For correct testing the APIs, you need an authorizing via JWT Token. Because all APIs are needed to be authorized.
First you need to get `access token` and `refresh token`. Use first APi for login `/token/`.
When you enter login and password in JSON format in field, like this:
```
{
  "username": "root",
  "password": "12345"
}
```
You will get a `access token` and `refresh token` which you can use for authorization in API testing.

Before make request you need to add `access token` into header field. Add token with keyword `Bearer`.
Like this -> `Bearer eyJhbGciOiJI...`.

If you got a message `Access token has been expired`, that means your `access token` the time of life has run out. You need to use `/refresh/` to update the token.
Enter the `refresh token` what you got with `access token` before.

## API Endpoints:
```
/swagger/ - For swagger documentation (test APIs via Swagger).
/token/ - For login registered user (return access and refresh tokens).
/token/refresh/ - To update the access token.
/admin/ - To enter the admin panel (you can register user here).
/weekly-schedule/ - Returns a JSON schedule of records for each day of the week based on the data in the DB.
/create-record/ - API for creating new record with timestamp. 
/delete-record/ - API for deleting record according to RECORD_ID (id = pk) in query_params.
/update-record/ - API for updating time (start time and/or end time). 
```