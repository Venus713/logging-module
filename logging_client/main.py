import json
import logging
from queue import Queue
from threading import Thread
from typing import List

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

    def info(self, thread_id: str, log_data: List[dict]) -> dict:
        """
        data should be a list of bellow data.
        {
            log_txt: str
            log_json: dict = {}
            log_attachment: str = None
            note: str = None
        }
        """

        t = Thread(target=self.log_task, args=(thread_id, log_data,))
        t.start()
        t.join()
        return {"message": "Successfully published"}

    def log_task(self, id: str, data: List[dict] = []) -> None:
        for d in data:
            context_data = self.context
            log_data = {
                "log_txt": d.get("log_txt"),
                "log_json": d.get("log_json", {}),
                "log_attachment": d.get("log_attachment"),
            }
            context_data["log_data"] = log_data
            context_data["note"] = d.get("note")
            context_data["thread_id"] = id

            logging.info(f"Received log_data: {context_data}")
            self.thread_1.queue.put(json.dumps(context_data))

    def terminate(self):
        self.thread_1.kill()
        self.thread_1.join()
