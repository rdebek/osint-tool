import os


class FileHandler:
    def __init__(self, dump_directory: str = 'gathered_data') -> None:
        self.dump_directory = dump_directory

    def save_person_info(self, person_name: str, person_data: str, info_source: str) -> None:
        if not os.path.exists(f'{self.dump_directory}/people/{person_name}'):
            os.makedirs(f'{self.dump_directory}/people/{person_name}', exist_ok=True)

        with open(f'{self.dump_directory}/people/{person_name}/{person_name}_{info_source}.txt', 'a',
                  encoding="utf-8") as f:
            f.write(person_data)
