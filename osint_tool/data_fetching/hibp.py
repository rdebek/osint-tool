from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = 'https://whatismyipaddress.com/breach-check'


class Hibp:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, "
            "like Gecko) "
            "Chrome/84.0.4147.125 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(),
                                       chrome_options=options)

    def check_if_pwned(self, email: str) -> str:
        self.driver.get(BASE_URL)
        self.driver.find_element(By.CLASS_NAME, value='css-47sehv').click()
        self.driver.find_element(By.ID, value='txtemail').send_keys(email)
        self.driver.find_element(By.ID, value='btnSubmit').click()
        if self.driver.find_element(By.ID, value='alertText').text:
            self.driver.close()
            return f'Provided email ({email}) does not appear to be valid.'
        if not self.driver.find_elements(By.CLASS_NAME, value='breach-wrapper'):
            self.driver.close()
            return f'No breaches found for {email}.'

        breaches = [breach.find_elements(By.CLASS_NAME, value='breach-item') for breach in
                    self.driver.find_elements(By.CLASS_NAME, value='breach-wrapper')]
        breaches_info = [[x.text for x in breach] for breach in breaches]
        self.driver.close()
        return self.format_pwn_info(breaches_info)

    @staticmethod
    def format_pwn_info(breaches_info: List[List[str]]) -> str:
        return_string = f'\nFound {len(breaches_info)} data breaches!'
        for i, breach in enumerate(breaches_info):
            return_string += f'\n\n{i + 1}.'
            for information_row in breach:
                return_string += f'\n{information_row}\n'
        return return_string
