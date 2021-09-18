from unittest import TestCase
from models import DomainNames, LinkRequest, DomainsResponse
import json

ID = "uuid-123"


class DomainNamesTest(TestCase):
    def test_get_domain_domains(self):
        links = [
            "ya.ru",
            "https://ya.ru/api/123",
            "https://google.com",
            "https://dog-shop.com/dogs?name=Billy"
        ]
        expected = {"domains": ["ya.ru", "ya.ru", "google.com", "dog-shop.com"], "uuid": ID}
        str_expected = json.dumps(expected)
        self.assertEqual(str_expected, LinkRequest.get_domain_names(links, ID).json())


class DomainsResponseTest(TestCase):
    def test_duplicated_domains_are_removed(self):
        domain_name_list = [
            DomainNames(domains=["ya.ru", "ya.ru", "google.com"], uuid="uuid-1"),
            DomainNames(domains=["google.com", "yahoo.com"], uuid="uuid-2")
        ]
        response = DomainsResponse.from_domains(domain_name_list)
        self.assertEqual(response.status, "ok")
        self.assertEqual(set(response.domains), {"ya.ru", "google.com", "yahoo.com"})
