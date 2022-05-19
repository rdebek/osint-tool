import requests
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
