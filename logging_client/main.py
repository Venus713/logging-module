import json
from queue import Queue

from .threads import PrimaryThread

q = Queue()


class Logger(object):
    def __init__(
        self, app_id, app_version_id, device_id, amqp_url, tbd=0, note=None
    ) -> None:
        self.app_id = app_id
        self.app_version_id = app_version_id
        self.device_id = device_id
        self.amqp_url = amqp_url
        self.note = note

        self.context = {
            "app_id": self.app_id,
            "app_version_id": self.app_version_id,
            "device_id": self.device_id,
            "note": self.note,
        }
        self.thread_1 = PrimaryThread(q, self.amqp_url)

    def info(self, request, msg, *args, **kwargs):
        self.context["log_msg"] = msg
        print(f"msg: {self.context}")
        self.thread_1.queue.put(json.dumps(self.context))
        return self.thread_1

    def terminate(self):
        self.thread_1.kill()
        self.thread_1.join()
