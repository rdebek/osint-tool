import os


class FileHandler:
    def __init__(self, dump_directory: str = 'gathered_data') -> None:
        self.dump_directory = dump_directory

    def save_person_info(self, person_name: str, person_data: str, info_source: str) -> None:
        self.create_directory(f'people/{person_name}')

        with open(f'{self.dump_directory}/people/{person_name}/{person_name}_{info_source}.txt', 'a',
                  encoding="utf-8") as f:
            f.write(person_data)

    def save_site_info(self, site_url: str, site_data: str, info_type: str) -> None:
        self.create_directory(f'sites/{site_url}')
        with open(f'{self.dump_directory}/sites/{site_url}/{site_url}_{info_type}.txt', 'a', encoding='utf-8') as f:
            f.write(site_data)

    def create_directory(self, directory_path: str) -> None:
        if not os.path.exists(f'{self.dump_directory}/{directory_path}'):
            os.makedirs(f'{self.dump_directory}/{directory_path}', exist_ok=True)

    def save_pwned_email(self, pwned_email: str, pwn_info: str):
        self.create_directory(f'pwned_emails/')
        with open(f'{self.dump_directory}/pwned_emails/{pwned_email}.txt', 'a', encoding='utf-8') as f:
            f.write(pwn_info)

    def save_gathered_emails(self, email_domain: str, emails: str):
        self.create_directory(f'gathered_emails/')
        with open(f'{self.dump_directory}/gathered_emails/{email_domain}.txt', 'a', encoding='utf-8') as f:
            f.write(emails)

    def save_gathered_numbers(self, number_prefix: str, numbers_found: str):
        self.create_directory(f'gathered_numbers/')
        with open(f'{self.dump_directory}/gathered_numbers/+{number_prefix}.txt', 'a', encoding='utf-8') as f:
            f.write(numbers_found)
