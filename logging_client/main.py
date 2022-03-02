import json
import logging
from queue import Queue

from .memory import RedisMemory
from .threads import PrimaryThread

q = Queue()
r = RedisMemory()


class Logger(object):
    def __init__(
        self,
        app_id: str,
        app_version_id: str,
        device_id: str,
        amqp_url: str,
        username: str,
        password: str,
    ) -> None:
        self.app_id = app_id
        self.app_version_id = app_version_id
        self.device_id = device_id
        self.amqp_url = amqp_url
        self.username = username
        self.password = password
        self.token = ""

        self.context = {
            "app_id": self.app_id,
            "app_version_id": self.app_version_id,
            "device_id": self.device_id,
            "username": self.username,
            "password": self.password,
        }

        """
        send a create_new_token message to the secondary thread
         via redis memory,
        But We need to discuss whether it is necessary.
        """
        user_credential = {
            "app_id": self.app_id,
            "username": self.username,
            "password": self.password,
        }
        r.save_data(user_credential, True)

        self.thread_1 = PrimaryThread(q, self.amqp_url)

    def info(
        self, log_txt: str, log_json: dict = {}, log_attachment: str = None, note=None
    ):
        log_data = {
            "log_txt": log_txt,
            "log_json": log_json,
            "log_attachment": log_attachment,
        }
        self.context["log_data"] = log_data
        self.context["note"] = note

        logging.info(f"Received log_data: {self.context}")
        self.thread_1.queue.put(json.dumps(self.context))
        return self.thread_1

    def terminate(self):
        self.thread_1.kill()
        self.thread_1.join()
