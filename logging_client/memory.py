import json
from typing import Any, Dict, Union

import redis


class RedisMemory:
    r = redis.Redis(decode_responses=True)
    create_msg = "Please get auth token!"
    update_msg = "Please update auth token!"

    def save_data(
        self,
        credential: Dict[str, str] = {},
        is_create: bool = True,
        is_update: bool = False,
        token: str = "",
        session_data: Dict[str, Union[float, str]] = {},
    ):
        self.r.set("credential", json.dumps(credential))
        self.r.set("create_msg", self.create_msg if is_create else "")
        self.r.set("update_msg", self.update_msg if is_update else "")
        self.r.set("token", token)
        self.r.set("session", json.dumps(session_data))

    def update_data(self, key: str, val: Union[str, Dict[str, Any]]):
        if isinstance(val, dict):
            val = json.dumps(val)
        return self.r.set(key, val)

    def get_data(self, key: str):
        return self.r.get(key)
