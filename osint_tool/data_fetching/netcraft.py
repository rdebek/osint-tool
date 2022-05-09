import re
from time import sleep
from typing import List, Tuple

from click import echo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

SUBDOMAINS_URL = 'https://searchdns.netcraft.com/'
SITE_REPORT_URL = 'https://sitereport.netcraft.com/?url={url}'


class NoSubDomainsFoundException(Exception):
    pass


class InvalidUrlFound(Exception):
    pass


class Netcraft:
    def __init__(self, url):
        options = Options()
        options.add_argument('--headless')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, "
            "like Gecko) "
            "Chrome/84.0.4147.125 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(),
                                       chrome_options=options)
        self.url = url

    def get_site_report(self) -> None:
        try:
            headers, data = self.gather_site_data()
        except InvalidUrlFound:
            return echo('Cannot generate site report for the provided url.')

        return echo(self.display_site_data(headers, data))

    def get_subdomains(self) -> None:
        try:
            number_of_subdomains, headers, structured_data = self.gather_subdomains()
        except NoSubDomainsFoundException:
            return echo('No subdomains found.')

        return echo(self.display_subdomains(number_of_subdomains, headers, structured_data))

    def get_site_technologies(self) -> None:
        echo('Looking for technologies used by the site...')
        sections = self.driver.find_elements(By.TAG_NAME, value='h2')
        for section in sections:
            if 'Site Technology' in section.text:
                tech_data = self.gather_technologies()
                return echo(self.display_technologies(tech_data))
        return echo('No technologies found.')

    def gather_technologies(self) -> List[Tuple]:
        technolgies_data = []
        tech_list = self.driver.find_element(By.CLASS_NAME, value='technology_list')
        table_bodys = tech_list.find_elements(By.TAG_NAME, value='tbody')
        for body in table_bodys:
            table_data = body.find_elements(By.TAG_NAME, value='td')
            for i, _ in enumerate(table_data):
                if (i + 1) % 3 == 1:
                    technolgies_data.append((table_data[i].text, table_data[i + 1].text))
        return technolgies_data

    def gather_site_data(self) -> Tuple[List[str], List[str]]:
        echo('Generating site report...')
        self.driver.get(SITE_REPORT_URL.format(url=self.url))
        error_string = self.driver.find_element(By.CLASS_NAME,
                                                value='banner__container--text').find_element(
            By.TAG_NAME,
            value='h2').text
        if error_string == 'Unable to report on this hostname as it does not resolve to an IP ' \
                           'address.':
            raise InvalidUrlFound
        sleep(1)
        info_tables = self.driver.find_elements(By.CLASS_NAME, value='table--multi')[:2]
        headers, data = [], []

        for table in info_tables:
            rows = table.find_elements(By.TAG_NAME, value='th')
            rows_data = table.find_elements(By.TAG_NAME, value='td')
            headers.extend([row.text for row in rows])
            data.extend([row_data.text for row_data in rows_data])

        return headers, data

    def gather_subdomains(self) -> Tuple[int, List[str], List[List[str]]]:
        echo('Looking for subdomains...')
        domain_name = self.get_domain_name()
        self.driver.get(SUBDOMAINS_URL)
        self.driver.find_element(By.NAME, value='host').send_keys(domain_name)
        self.driver.find_element(By.CLASS_NAME, value='contact-form__submit').click()
        results_string = self.driver.find_element(By.CLASS_NAME,
                                                  value='banner__container--text').find_element(
            By.TAG_NAME, value='h2').text
        if 'First' in results_string:
            number_of_subdomains_found = int(results_string.split(" ")[1])
        else:
            try:
                number_of_subdomains_found = int(results_string.split(" ")[0])
            except ValueError as err:
                raise NoSubDomainsFoundException from err
        echo(f'Displaying subdomains for {domain_name}')
        headers = [row.text for row in
                   self.driver.find_element(By.TAG_NAME, value='tr').find_elements(By.TAG_NAME,
                                                                                   value='th')]
        data_rows = [x.find_elements(By.TAG_NAME, value='td') for x in
                     self.driver.find_element(By.TAG_NAME, value='tbody').find_elements(By.TAG_NAME,
                                                                                        value='tr')]

        structured_data = []

        for arr in data_rows:
            helper_array = []
            for item in arr:
                helper_array.append(item.text)
            structured_data.append(helper_array[1:-1])

        return number_of_subdomains_found, headers[1: -1], structured_data

    def get_domain_name(self) -> str:
        modified_url = ''
        if 'http' in self.url:
            modified_url = self.url[self.url.find('/') + 2:]
        dot_indexes = [m.start() for m in re.finditer('\\.', modified_url)]
        return modified_url[dot_indexes[-2]:] if len(dot_indexes) >= 2 else modified_url

    @staticmethod
    def display_technologies(technologies_data: List[Tuple]) -> str:
        return_str = '\n'
        for tech_name, tech_description in technologies_data:
            return_str += f'{tech_name} - {tech_description}\n'
        return return_str

    @staticmethod
    def display_subdomains(number_of_subdomains: int, headers: List[str],
                           data: List[List[str]]) -> str:
        return_str = f'\nFound {number_of_subdomains} subdomains!\n\nShowing 20 most popular ' \
                     f'subdomains found:\n\n'
        for j, row in enumerate(data):
            return_str += f'{j + 1}. '
            for i, column in enumerate(row):
                if i == 0:
                    return_str += f'{column} | '
                else:
                    return_str += f'{headers[i]}: {column} | '
            return_str += '\n'
        return return_str

    @staticmethod
    def display_site_data(headers: List[str], data: List[str]) -> str:
        return_str = '\n'
        for header, data_row in zip(headers, data):
            if header:
                return_str += f'{header}: {data_row}\n'
        return return_str
