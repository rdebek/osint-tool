import json
from collections import defaultdict
from os import environ
from osint_tool.util.file_handler import FileHandler
from click import echo, prompt, confirm
from linkedin_api import Linkedin as linkedin_api
from typing import List, Tuple
from osint_tool.util.errors import NoLinkedinProfileFound

LINKEDIN_LOGIN = environ.get('LINKEDIN_LOGIN')
LINKEDIN_PASS = environ.get('LINKEDIN_PASS')


class Linkedin:
    def __init__(self):
        self.api = linkedin_api(LINKEDIN_LOGIN, LINKEDIN_PASS)
        self.file_handler = FileHandler()

    def get_person_report(self, person: str) -> None:
        info_dict = self.prompt_additional_info()
        try:
            profile_id = self.get_profile_id(person, info_dict)
        except NoLinkedinProfileFound:
            return echo(f'No linkedin profile found for {person}.')
        profile_info = self.get_profile_info(profile_id)
        profile_info_formatted = self.format_profile_info(profile_info)
        self.file_handler.save_person_linkedin_info(person, profile_info_formatted)
        echo(profile_info_formatted)
        self.handle_companies_info(self.get_companies(profile_info))

    def get_profile_info(self, profile_id: str) -> defaultdict:
        echo('Retrieving profile information...')
        return defaultdict(str, self.api.get_profile(public_id=profile_id))

    def get_profile_id(self, person: str, info_dict: defaultdict = None) -> str:
        echo('Getting Linkedin profile ID...')
        info_dict = info_dict if info_dict else defaultdict(str)

        people_found = self.api.search_people(person, keyword_company=info_dict['company_name'],
                                              keyword_school=info_dict['school_name'],
                                              keyword_title=info_dict['job_title'])
        if not people_found:
            raise NoLinkedinProfileFound

        return people_found[0]['public_id']

    def handle_companies_info(self, companies):
        if not companies:
            return
        if confirm(f'Gather information about companies?'):
            echo(f'Companies found: \n')
            [echo(f'- {company_name}') for company_name, _ in companies]
            for company, company_id in companies:
                info = self.get_company_info(company, company_id)
                self.format_company_info(info)

    def get_company_info(self, company_name: str, company_id) -> defaultdict:
        echo(f'Gathering information about {company_name}...')
        company_info = self.api.get_company(company_id[company_id.rfind(':') + 1:])
        return defaultdict(str, company_info)

    def format_company_info(self, company_info: defaultdict) -> str:
        json.dumps(company_info, indent=2)
        return 'temp'

    @staticmethod
    def get_companies(info_dict: defaultdict) -> List[Tuple]:
        companies = []
        for job in info_dict['experience']:
            company_id = job['companyUrn'][job['companyUrn'].rfind(":") + 1:]
            companies.append((job['companyName'], company_id))
        return companies

    @staticmethod
    def prompt_additional_info() -> defaultdict:
        echo('Please provide additional information (leave blank if unknown)')
        info_dict = defaultdict(str)
        info_dict['company_name'] = prompt('Company name', default='', show_default=False)
        info_dict['school_name'] = prompt('School name', default='', show_default=False)
        info_dict['job_title'] = prompt('Job title', default='', show_default=False)
        return info_dict

    @staticmethod
    def format_profile_info(profile_info: defaultdict) -> str:
        profile_name = f'\n{profile_info["firstName"].upper()} {profile_info["lastName"].upper()}\n'
        general_info = "\nGENERAL INFORMATION\n"
        general_info += f"Industry: {profile_info['industryName']}\n" \
                        f"Current role: {profile_info['headline']}\n" \
                        f"Location: {profile_info['locationName']}\n" \
                        f"Summary: {profile_info['summary']}\n"
        experience_info = "\nEXPERIENCE INFORMATION\n"
        for job in profile_info['experience']:
            job = defaultdict(str, job)
            job["timePeriod"] = defaultdict(str, job["timePeriod"])
            experience_info += f'\n{job["companyName"]}\n' \
                               f'Job title: {job["title"]}\n' \
                               f'Start date: {job["timePeriod"]["startDate"]["month"] if job["timePeriod"]["startDate"] else "--"}/' \
                               f'{job["timePeriod"]["startDate"]["year"] if job["timePeriod"]["startDate"] else "--"}\n' \
                               f'End date: ' \
                               f'{job["timePeriod"]["endDate"]["month"] if job["timePeriod"]["endDate"] else "--"}/' \
                               f'{job["timePeriod"]["endDate"]["year"] if job["timePeriod"]["endDate"] else "--"}\n' \
                               f'Description:{job["description"] if job["description"] else "-----"}\n'

        education_info = "\nEDUCATION INFORMATION\n"
        for school in profile_info["education"]:
            school = defaultdict(str, school)
            school["timePeriod"] = defaultdict(str, school["timePeriod"])
            education_info += f'\n{school["schoolName"]}\n' \
                              f'Start date: {school["timePeriod"]["startDate"]["year"]}\n' \
                              f'End date: ' \
                              f'{school["timePeriod"]["endDate"]["year"] if school["timePeriod"]["endDate"] else "---"}\n' \
                              f'Degree name: {school["degreeName"]}\n' \
                              f'Field of study: {school["fieldOfStudy"]}\n'

        return profile_name + general_info + experience_info + education_info
