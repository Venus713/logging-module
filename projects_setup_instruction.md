# Projects Setup Instructions

## Client Component

`logging-client` is a Python client for logging message in a Python applications.
`logging-client` is one part of our `Logging System`.

### Installation

#### Minimum Requirements

- python3.x

#### Installing with `pip`

    ```
    $ pip install git+git://github.com/Venus713/logging-module.git
    ```

#### `Logger` object

`Logger` object has the following attributes:

- app_id: a unique identifier for an application
- app_version_id: a unique identifier for a version of that application
- device_id: a unique identifier for the device executing the application
- amqp_url: a rabbitmq broker url

#### How to use it?

    ```
    logger = Logger(
        app_id=<your app id>,
        app_version_id=<your app version>,
        device_id=<your device id>,
        amqp_url=<your broker url>,
        username=<your username>,
        password=<your password>
    )
    logger.info(
        thread_id,
        [
            {
            'log_txt': <your log text>,
            'log_json': <your log json>,
            'log_attachment': <your attachment file path>
            },
            ...
        ]
    )
    ```

## Server Component

This is a second part of our `Logging System`, and it communicates with webserver component from the `client component`.

### pre-requisite

- python3.x
- virtualenv

### How to run locally?

- clone project from git

        ```
        $ git clone https://github.com/Venus713/server-component.git
        $ cd server-component
        $ pip install -r requirements.txt
        ```
- copy/paste `.env` from `.env.example` and config `.env`

        ```
        $ cp .env.example .env
        ```
- run kafka

        ```
        $ make run-kafka
        ```
- run app in another terminal

        ```
        $ source venv/bin/activate
        $ make run-app
        ```

### WebServer Component

This is a third part of our `Logging System`, and retrieve information from Kafka and displays the information in response to requests from web browser.

### Pre-requisite

- python3
- virtualenv

### How to run it locally?

- clone a project from git

        ```
        $ git clone https://github.com/Venus713/Webserver-Component.git
        ```
- install pip

        ```
        $ cd webserver-component
        $ pip install -r requirements.txt
        ```
- copy/paste `.env` from `.env.example` and config the `.env`

        ```
        $ cp .env.example .env
        ```
- run kafka

        ```
        $ make run-kafka
        ```
- run webserver

        ```
        $ make run-server
        ```
- run celery

        ```
        $ make run-celery
        ```
- run celery-beat

        ```
        $ make run-celery-beat
        ```

## Heartbeat Component

This is a fourth part of our `Logging System`, and it checks the health of the server-side components: `FastAPI`, `Kafka`, `Django`, `Celery`, `PostgreSQL`, `RabbitMQ`.

### pre-requisites

- python3.x
- virtualenv

### How to run it locally

- clone project from git repository

        ```
        $ git clone https://github.com/Venus713/heartbeat-component.git
        ```

- copy/paste `.env` from `.env.example` and config the `.env`

        ```
        $ cd heartbeat-component
        $ cp .env.example .env
        ```

- install pip

        ```
        $ pip install -r requirements.txt
        ```

- run app

        ```
        $ source venv/bin/activate
        $ python run.py
        ```

Note: Please make sure that `2181` and `9002` ports is not used by another service in your server.
And If you are running the `server-component` and `webserver-component` in one server, then you should run only one `kafka` service. In other words, if you run the `kafka` in the `server-component`, then you can skip to run the `kafka` in the `webserver-component`.
