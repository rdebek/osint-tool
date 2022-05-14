import os


class FileHandler:
    def __init__(self, dump_directory: str = 'gathered_data') -> None:
        self.dump_directory = dump_directory

    def save_person_linkedin_info(self, person_name: str, person_data: str) -> None:
        if not os.path.exists(f'{self.dump_directory}/people/{person_name}'):
            os.makedirs(f'{self.dump_directory}/people/{person_name}', exist_ok=True)

        with open(f'{self.dump_directory}/people/{person_name}/{person_name}_linkedin.txt', 'a') as f:
            f.write(person_data)



