import re
from typing import List

import requests
import unicodedata
from bs4 import BeautifulSoup
from click import echo
from googlesearch import search

from osint_tool.util.file_handler import FileHandler


class Google:

    def __init__(self):
        self.file_handler = FileHandler()

    def get_emails(self, email_domain: str) -> None:
        emails = self.gather_emails(email_domain)
        if not emails:
            return echo(f"Didn't find any emails from {email_domain}.")
        formatted_emails = self.format_emails(emails, email_domain)
        self.file_handler.save_gathered_emails(email_domain, formatted_emails)
        return echo(formatted_emails)

    @staticmethod
    def gather_emails(email_domain: str) -> set:
        query = f'intext:@{email_domain}'
        urls_found = search(query, num=10, stop=10, pause=2)
        emails_found = []
        for url in urls_found:
            page_src = requests.get(url, verify=False).text
            soup = BeautifulSoup(page_src, 'lxml')
            emails_found.extend(soup(text=lambda t: f"@{email_domain}" in t))
        return set(emails_found)

    @staticmethod
    def sanitize_email(email: str, email_domain: str) -> str:
        email_split = email.split(' ')

        if len(email_split) > 1:
            for string in email_split:
                if '@' in string:
                    email = string

        email = email.strip()

        if not email.endswith(email_domain):
            email = email[:email.find(email_domain) + len(email_domain)]

        return email

    def format_emails(self, emails: set, email_domain: str):
        echo(f'Found {len(emails)} emails!')
        return_str = ''
        for email in emails:
            email = self.sanitize_email(email, email_domain)
            return_str += f'- {email}\n'
        return return_str

    # def get_person_email(self, person: str):
    #     regex = '([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    #     query = f'intext:"{person}" AND intext:"mail"'
    #     urls_found = search(query, num=10, stop=10, pause=2)
    #     emails_found = []
    #     for url in urls_found:
    #         page_src = requests.get(url, verify=False).text
    #         soup = BeautifulSoup(page_src, 'lxml')
    #         emails_found.extend(soup)

    # emails_found.extend(soup(text=lambda t: "@" in t))
    # print(emails_found)

    def get_phone_numbers(self, number_prefix: str) -> None:
        numbers_found = self.gather_phone_numbers(number_prefix)
        formatted_numbers = self.format_numbers(numbers_found)
        self.file_handler.save_gathered_numbers(number_prefix, formatted_numbers)
        echo(formatted_numbers)

    def gather_phone_numbers(self, number_prefix: str):
        query = f'intext:"+{number_prefix}"'
        urls_found = search(query, num=10, stop=10, pause=5, user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X '
                                                                        '10_11_5)\
            AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36')
        numbers_found = []
        for url in urls_found:
            page_src = requests.get(url, verify=False).text
            soup = BeautifulSoup(page_src, 'lxml')
            numbers_found.extend(soup(text=lambda t: f"+{number_prefix}" in t))

        sanitized_numbers = []
        for number in numbers_found:
            sanitized_numbers.extend(self.sanitize_number(number_prefix, number))
        return list(set(sanitized_numbers))

    @staticmethod
    def sanitize_number(prefix: str, phone_number: str) -> List[str]:
        stripped_number = unicodedata.normalize('NFKC', phone_number).replace(' ', '')
        numbers_found = re.findall('[0-9]+', stripped_number)
        sanitized_numbers = []
        for number in numbers_found:
            if len(number) != len(prefix) + 9:
                return []
            sanitized_numbers.append(number[number.find(prefix) + len(prefix):])
        return sanitized_numbers

    @staticmethod
    def format_numbers(numbers_array: List[str]) -> str:
        echo(f'Found {len(numbers_array)} numbers!\n')
        return_str = ''
        for number in numbers_array:
            return_str += f'- {number}\n'
        return return_str
