# logging-client

`logging-client` is a Python client for logging message in a Python applications.
`logging-client` is one part of our `Logging System`.

## Installation

### Minimum Requirements

- python3.x

### Installing with `pip`

    ```
    $ pip install git+git://github.com/Venus713/logging-module.git
    ```

### `Logger` object

`Logger` object has the following attributes:

- app_id: a unique identifier for an application
- app_version_id: a unique identifier for a version of that application
- device_id: a unique identifier for the device executing the application
- amqp_url: a rabbitmq broker url

### How to use it?

    ```
    logger = Logger(
        app_id=<your app id>,
        app_version_id=<your app version>,
        device_id=<your device id>,
        amqp_url=<your broker url>
    )
    logger.info(request, <your message text>, <your note>)
    ```
