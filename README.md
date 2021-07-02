Project Service
================

The Unikube project service.


Authentication
==============
```bash
curl --location --request POST 'http://localhost:8000/api/token/' \
--header 'Content-Type: application/json' \
--data-raw '{"username": "admin", "password": "test"}'
```

After this run requests with the retrieved access token against the `/graphql` endpoint:

```
curl --location --request POST 'localhost:8000/graphql' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTg1NDg5Mjk5LCJqdGkiOiJhZjgwMDU2YTBmNGQ0M2JhOTFiN2UyNGMzYjBlNDU3ZiIsInVzZXJfaWQiOjF9.6PJnqksrQ5UOPuE8e3vDU8gAxZejFP4MXps0tzuuXh4' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=GV5XLgjEtrrNq2u505dtLgRDhZpbYwE9UmeAqiYp4NmQ5WsZ6HVG9HXZEywsqCtB' \
--data-raw '{"query":"query {\n    projects {\n        id      \n    }\n}","variables":{}}'
```


For development purposes one may log into the Django admin interface and use
the `/graphql` endpoint through the browser.

# Development Setup
We're using [black](https://github.com/psf/black). It helps us keep the code style
aligned throughout the project.

To make sure your code is well formatted, please install [pre-commit](https://pre-commit.com/). 
After that just run `pre-commit install` in the repositories root directory.

# Testing
Run tests:

```shell
coverage run --source='.' manage.py test
coverage report
```

