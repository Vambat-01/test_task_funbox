import time
from unittest import TestCase
import requests
from requests.models import Response
from server import get_unix_time
import json
from typing import Set, List


class SystemTest(TestCase):
    """
        Для запуска теста должны быть запущены web-приложение и redis.
    """
    def _post_links(self, links: List[str]) -> Response:
        url = "http://0.0.0.0:8000/visited_links"
        return requests.post(url, json={"links": links})

    def _get_domains(self, from_: float, to: float) -> dict:
        response = requests.get(f"http://0.0.0.0:8000/visited_domains?from={from_}&to={to}")
        self.assertEqual(response.status_code, 200)
        return response.json()

    def _check_domains(self, from_: float, to: float, expected: Set[str]):
        body = self._get_domains(from_, to)
        self.assertEqual(body["status"], "ok")
        self.assertEqual(set(body["domains"]), expected)

    def test_web_app(self):
        # отправляем ссылки
        self.assertEqual(self._post_links(["https://before.com", "before-two.ru/foo/?query=x"]).status_code, 200)
        
        time.sleep(1)
        start_time_sec = get_unix_time()
        time.sleep(1)

        self.assertEqual(self._post_links(["ya.ru", "https://ya.ru", "google.com"]).status_code, 200)
        self.assertEqual(self._post_links(["google.com", "https://yahoo.com"]).status_code, 200)

        time.sleep(1)
        end_time_sec = get_unix_time()
        time.sleep(1)
        
        self.assertEqual(self._post_links(["after.org/1", "after.org/2"]).status_code, 200)

        # проверяем домены
        self._check_domains(start_time_sec - 5, start_time_sec, {"before.com", "before-two.ru"})
        self._check_domains(start_time_sec, end_time_sec, {"ya.ru", "google.com", "yahoo.com"})
        self._check_domains(end_time_sec, end_time_sec + 5, {"after.org", "after.org"})

    def test_validation_exception(self):
        links = ["/funbox.ru", "https://world-weather.com", "https://google.ru/maps"]
        expected_error_text = {
            "status": [
                "/funbox.ru",
                "https://world-weather.com",
                "https://google.ru/maps"
            ]
        }
        str_error = json.dumps(expected_error_text)
        response = self._post_links(links)
        self.assertEqual(response.status_code, 400)
        request_text = json.dumps(response.json())
        self.assertEqual(str_error, request_text)
