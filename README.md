# logging-client

`logging-client` is a Python client for logging message in a Python applications.
`logging-client` is one part of our `Logging System`.

## How to develope?

- Locally install after updating this package in development

```bash
pip install -e .
```

- build after updating

```bash
python setup.py install
```

## Installation

### Minimum Requirements

- python3.x

### Installing with `pip`

```bash
pip install git+git://github.com/Venus713/logging-module.git
```

### `Logger` object

`Logger` object has the following attributes:

- app_id: a unique identifier for an application
- app_version_id: a unique identifier for a version of that application
- device_id: a unique identifier for the device executing the application
- amqp_url: a rabbitmq broker url

### How to use it?

```python
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

`Note`: Make sure that `RabbitMQ` and `Redis` server is running on your system.
