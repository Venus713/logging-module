import json
import os
from datetime import datetime
from typing import Any, Dict

import requests

from .config import Settings
from .exceptions import APIClientException
from .memory import RedisMemory

r = RedisMemory()
settings: Settings = Settings()


class APIClients:
    def __init__(self, thread_id: str = None) -> None:
        self.headers: Dict = {}

        self.thread_id = thread_id

        self.__credential = json.loads(r.get_data("credential"))
        self.__token: str = r.get_data("token")
        self.is_create_token: bool = True if r.get_data("create_msg") else False
        self.is_update_token: bool = True if r.get_data("update_msg") else False

        self.is_token_expired: bool = False

        self.__session_id: str = None
        self.is_session_expired: bool = True

        self.session_data = r.get_data("session")
        if self.session_data:
            self.__session_id: str = json.loads(self.session_data).get("session_id")
            self.__session_exp_time: float = json.loads(self.session_data).get(
                "exp_time"
            )
            if self.__session_exp_time:
                self.is_session_expired: bool = False if (
                    self.__session_exp_time >= datetime.utcnow().timestamp()
                ) else True

        self.signup_url = f"{settings.api_base_endpoint}/signup"
        self.login_url = f"{settings.api_base_endpoint}/login"
        self.session_url = f"{settings.api_base_endpoint}/session"
        self.log_url = f"{settings.api_base_endpoint}/log"
        self.hearbeat_url = f"{settings.api_base_endpoint}/health"

    @property
    def auth_token(self) -> str:
        # here get username and password from redis memory
        # and call the fourth api to get auth token
        if not self.__token or self.is_token_expired or self.is_update_token:
            self.__token = self.get_auth_token()

        return self.__token

    def __get_default_headers(self):
        self.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.__token}",
                "session_id": self.__session_id,
            }
        )
        return self.headers

    def __get_response_data(self, response):
        try:
            return response.json()
        except Exception as e:
            print(f"error in __get_response_data: {e}")
            message = f"JSON decode error. {response.content}"
            raise APIClientException(
                message=message,
                status_code=response.status_code,
                response_data=str(response.content),
            )

    def __request(
        self, method, url, headers=None, params=None, data=None, json=None, **kwargs
    ):
        if headers is None:
            headers = self.__get_default_headers()

        response = requests.request(
            method, url, headers=headers, params=params, data=data, json=json, **kwargs
        )

        if url == self.signup_url and response.status_code == 400:
            r.update_data("create_msg", "")
            self.is_create_token = False

        if response.status_code in [401, 403]:
            print(f"token has been expired in calling {url}")
            self.is_token_expired = True
            self.get_auth_token()
            self.__request(
                method=method, url=url, headers=headers, data=data, json=json
            )

        if response.status_code not in [200, 201, 202, 203, 204, 205, 206]:
            print(
                "status_code is not [200, 201, 202, 203, 204, 205, 206] " "in __request"
            )
            raise APIClientException(
                message=f"response status code = {response.status_code}",
                status_code=response.status_code,
                response_data=str(response.content),
            )

        response_data = self.__get_response_data(response)
        return response_data

    def get_auth_token(self):
        # please add more exception handling here

        self.__credential["thread_id"] = self.thread_id

        if self.is_create_token:
            try:
                print("calling signup api")
                resp = self.__request("POST", self.signup_url, json=self.__credential)
                self.__token = resp.get("access_token")
                r.update_data("token", self.__token)
                r.update_data("create_msg", "")
                self.is_create_token = False
            except Exception as e:
                print(f"exception in calling signup api: {e}")
                self.is_update_token = True
                r.update_data("create_msg", "")
                self.is_create_token = False
                self.get_auth_token()
        elif self.is_token_expired or not self.__token:
            print("calling signin api")
            resp = self.__request("POST", self.login_url, json=self.__credential)
            self.__token = resp.get("access_token")
            r.update_data("token", self.__token)

            r.update_data("update_msg", "")
            self.is_create_token = False

            r.update_data("create_msg", "")
            self.is_update_token = False
        print(f"current token: {self.__token}")
        return self.__token

    def get_session_id(self, data: Dict[str, str]) -> str:
        # please add exception handling here

        if self.is_session_expired or not self.__session_id:
            print("calling session api")
            resp = self.__request("POST", self.session_url, json=data)
            self.__session_id = resp.get("session_id")
            r.update_data("session", resp)
        print(f"current session_id: {self.__session_id}")
        return self.__session_id

    def send_log(self, data: Dict[str, Any]) -> str:
        # please add an exception handling here

        self.get_auth_token()
        session_data = {
            "app_id": data.get("app_id"),
            "app_version_id": data.get("app_version_id"),
            "device_id": data.get("device_id"),
            "note": data.get("note"),
            "thread_id": data.get("thread_id"),
        }
        self.get_session_id(session_data)

        log_data = data.get("log_data")
        log_data["thread_id"] = data.get("thread_id")
        if log_data.get("log_attachment"):
            file_contents = (
                open(log_data["log_attachment"], "rb").read().decode(errors="ignore")
            )
            filename = os.path.basename(log_data.get("log_attachment"))
            log_data["log_attachment"] = {
                "file_content": file_contents,
                "file_name": filename,
            }
        else:
            log_data["log_attachment"] = {"file_content": None, "file_name": None}
        if log_data.get("log_text"):
            log_data["log_txt"] = log_data["log_text"]

        print(f"calling log api: {log_data}")
        resp = self.__request("POST", self.log_url, json=log_data)
        transaction_id = resp.get("transaction_id")
        print(f"current transaction id: {transaction_id}")

        return transaction_id
