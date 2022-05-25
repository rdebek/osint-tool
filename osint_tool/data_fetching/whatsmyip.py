from typing import List

from click import echo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from osint_tool.util.file_handler import FileHandler

BASE_URL = 'https://whatismyipaddress.com/breach-check'


class Whatsmyip:
    def __init__(self, email: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, "
            "like Gecko) "
            "Chrome/84.0.4147.125 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(),
                                       chrome_options=options)
        self.file_handler = FileHandler()
        self.email = email

    def check_if_pwned(self) -> str:
        self.driver.get(BASE_URL)
        self.driver.find_element(By.CLASS_NAME, value='css-1hy2vtq').click()
        self.driver.find_element(By.ID, value='txtemail').send_keys(self.email)
        self.driver.find_element(By.ID, value='btnSubmit').click()
        if self.driver.find_element(By.ID, value='alertText').text:
            self.driver.close()
            return f'Provided email ({self.email}) does not appear to be valid.'
        if not self.driver.find_elements(By.CLASS_NAME, value='breach-wrapper'):
            self.driver.close()
            return f'No breaches found for {self.email}.'

        breaches = [breach.find_elements(By.CLASS_NAME, value='breach-item') for breach in
                    self.driver.find_elements(By.CLASS_NAME, value='breach-wrapper')]
        breaches_info = [[x.text for x in breach] for breach in breaches]
        self.driver.close()
        return self.format_pwn_info(breaches_info)

    def format_pwn_info(self, breaches_info: List[List[str]]) -> str:
        echo(f'\nFound {len(breaches_info)} data breaches!')
        return_string = ''
        for i, breach in enumerate(breaches_info):
            return_string += f'\n{i + 1}.'
            for information_row in breach:
                return_string += f'\n{information_row}\n'
        self.file_handler.save_pwned_email(self.email, return_string)
        return return_string
