class APIClientException(Exception):
    def __init__(self, message, status_code, response_data):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self):
        return str(self.message)
