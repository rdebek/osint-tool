from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
from typing import List

SUBDOMAINS_URL = 'https://searchdns.netcraft.com/'


class Netcraft:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.125 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), chrome_options=options)

    def get_subdomains(self, url: str) -> str:
        domain_name = self.get_domain_name(url)
        self.driver.get(SUBDOMAINS_URL)
        self.driver.find_element(By.NAME, value='host').send_keys(domain_name)
        self.driver.find_element(By.CLASS_NAME, value='contact-form__submit').click()
        results_string = self.driver.find_element(By.CLASS_NAME, value='banner__container--text').find_element(
            By.TAG_NAME, value='h2').text
        try:
            number_of_subdomains_found = int(results_string.split(" ")[0])
        except ValueError:
            return 'No subdomains found'

        headers = [row.text for row in
                   self.driver.find_element(By.TAG_NAME, value='tr').find_elements(By.TAG_NAME, value='th')]
        data_rows = [x.find_elements(By.TAG_NAME, value='td') for x in
                     self.driver.find_element(By.TAG_NAME, value='tbody').find_elements(By.TAG_NAME, value='tr')]

        structured_data = []

        for arr in data_rows:
            helper_array = []
            for item in arr:
                helper_array.append(item.text)
            structured_data.append(helper_array[1:-1])

        return self.format_subdomains_info(number_of_subdomains_found, headers[1: -1], structured_data)

    @staticmethod
    def get_domain_name(url: str) -> str:
        dot_indexes = [m.start() for m in re.finditer('\\.', url)]
        if len(dot_indexes) < 2:
            return url
        return url[dot_indexes[-2]:]

    @staticmethod
    def format_subdomains_info(number_of_subdomains: int, headers: List[str], data: List[List[str]]) -> str:
        return_str = f'\nFound {number_of_subdomains} subdomains!\n\nShowing 20 most popular subdomains found:\n\n'
        for j, row in enumerate(data):
            return_str += f'{j + 1}. '
            for i, column in enumerate(row):
                if i == 0:
                    return_str += f'{column} | '
                else:
                    return_str += f'{headers[i]}: {column} | '
            return_str += '\n'
        return return_str
