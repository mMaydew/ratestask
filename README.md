# Xeneta rates task

We are provided a postgres database as a docker container.

The task is as follows:
```
Develop an HTTP-based API capable of handling the GET request described below. Our stack is based on Flask, but you are free to choose any Python framework you like. All data returned is expected to be in JSON format. Please demonstrate your knowledge of SQL (as opposed to using ORM querying tools).

Implement an API endpoint that takes the following parameters:
    date_from
    date_to
    origin
    destination

and returns a list with the average prices for each day on a route between port codes origin and destination. Return an empty value (JSON null) for days on which there are less than 3 prices in total.

Both the origin, destination params accept either port codes or region slugs, making it possible to query for average prices per day between geographic groups of ports.
```


# Initial setup

Create the containers for postgres and the API:
```bash
docker-compose up -d --build
```

The API will be available at `127.0.0.1:80`

# Testing

* Windows:
```bash
py -m pip install -U pytest
py -m pytest --verbose
```

* Unix based systems:
```bash
pip3 install -U pytest
pytest --verbose
```