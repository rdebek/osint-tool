from collections import defaultdict
from typing import List, Tuple

from click import confirm, echo, prompt
from linkedin_api import Linkedin as LinkedinApi

from osint_tool.util.credentials_manager import LINKEDIN_LOGIN, LINKEDIN_PASS
from osint_tool.util.errors import NoLinkedinProfileFound
from osint_tool.util.file_handler import FileHandler


class Linkedin:
    def __init__(self):
        self.api = LinkedinApi(LINKEDIN_LOGIN, LINKEDIN_PASS)
        self.file_handler = FileHandler()

    def get_person_report(self, person: str) -> None:
        info_dict = self.prompt_additional_info()
        try:
            profile_id = self.get_profile_id(person, info_dict)
        except NoLinkedinProfileFound:
            echo(f'No linkedin profile found for {person}.')
            return
        profile_info = self.get_profile_info(profile_id)
        profile_info_formatted = self.format_profile_info(profile_info)
        self.file_handler.save_person_info(person, profile_info_formatted, 'linkedin')
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
        if confirm('Gather information about companies?'):
            echo('Companies found:')
            for company_name, _ in companies:
                echo(f'- {company_name}')

            for company, company_id in companies:
                info = self.get_company_info(company, company_id)
                formatted_info = self.format_company_info(info)
                echo(formatted_info)
                self.file_handler.save_company_info(company, formatted_info)

    def get_company_info(self, company_name: str, company_id) -> defaultdict:
        echo(f'Gathering information about {company_name}...')
        company_info = self.api.get_company(company_id[company_id.rfind(':') + 1:])
        return defaultdict(str, company_info)

    def format_company_info(self, company_info: defaultdict) -> str:
        return_str = ''
        locations = self.format_location_info(company_info["confirmedLocations"])
        description = company_info["description"].replace("\n", "")
        return_str += f'{company_info["name"]}\n' \
                      f'Website: {company_info["callToAction"]["url"]}\n' \
                      f'Number of employees: {company_info["staffCount"]}\n' \
                      f'Locations: \n\n{locations}' \
                      f'Specializes in: {", ".join(company_info["specialities"])}\n' \
                      f'Description: {description}\n'
        return return_str

    @staticmethod
    def format_location_info(locations_array: List[dict]) -> str:
        locations_info = ''
        for i, location in enumerate(locations_array):
            locations_info += f'{i + 1}.\n' \
                              f'Country: {location.get("country", "")}\n' \
                              f'Geographic area: {location.get("geographicArea", "")}\n' \
                              f'City: {location.get("city", "")}\n' \
                              f'Address: ' \
                              f'{location.get("line1", "").strip() + " " + location.get("line2", "").strip()}\n\n'
        return locations_info

    @staticmethod
    def get_companies(info_dict: defaultdict) -> List[Tuple]:
        companies = []
        for job in info_dict['experience']:
            job = defaultdict(str, job)
            if job['companyUrn'] and job['companyName']:
                company_id = job['companyUrn'][job['companyUrn'].rfind(":") + 1:]
                companies.append((job['companyName'], company_id))
        return list(set(companies))

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

        if profile_info['experience']:
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
        else:
            experience_info = ''

        if profile_info['education']:
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
        else:
            education_info = ''

        return profile_name + general_info + experience_info + education_info
