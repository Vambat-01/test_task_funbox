from pydantic import BaseModel
from typing import List
from dataclasses import dataclass
from urllib.parse import urlparse
import validators


class ValidationException(Exception):
    """
        Ошибка валидации ссылки
    """

    def __init__(self, name: List[str]):
        self.name = name


class DomainNames(BaseModel):
    """
        Модель доменных имен для хранения в Redis
    """
    domains: List[str]
    uuid: str

    @staticmethod
    def parse_bytes(data: bytes) -> 'DomainNames':
        data_str = data.decode('utf-8')
        return DomainNames.parse_raw(data_str) 


class LinkRequest(BaseModel):
    """
        Тело запроса на добавление ссылок
    """
    links: List[str]

    @staticmethod
    def get_domain_names(links: List[str], id: str) -> 'DomainNames':
        """
            Получает домменные имена сайтов
        :param links: список ссылок
        :param id: уникальный идентификатор. В "POST" запросе могут прийти одинаковые данные посещения сайтов, но в разное
                   время. Чтобы при добавления записи в Redis "вторая" запись не перетерла "первую", в список посещенных
                   сайтов добавлен уникальный идентификатор
        :return: доменные имена с уникальным идентификатором
        """
        domain_names = []
        for link in links:
            domain_name = urlparse(link).netloc
            if not domain_name:
                validation_names = "https://" + link
                domain_name = urlparse(validation_names).netloc

            check_validation = validators.url("https://" + domain_name)
            if check_validation:
                domain_names.append(domain_name)
            else:
                # Если в запросе присутствует невалидная ссылка у которой не определяется
                # доменное имя, то будет вызвано исключение
                raise ValidationException(links)

        return DomainNames(domains=domain_names, uuid=id)


@dataclass(frozen=True)
class DomainsResponse:
    """
        Ответ сервера на запрос посещенных доменов
    """
    domains: List[str]
    status: str

    @staticmethod
    def from_domains(domain_names_list: List[DomainNames]) -> "DomainsResponse":
        """
            Возвращает ответ сервера без дубликатов и id
        :param domain_names: список доменных имен
        """
        domains = set()
        for domain_names in domain_names_list:
            for name in domain_names.domains:
                domains.add(name)
        
        return DomainsResponse(list(domains), "ok")
