from os import environ
from typing import List

import tweepy
from click import echo

from osint_tool.util.errors import NoTwitterProfileFound
from osint_tool.util.file_handler import FileHandler

BEARER_TOKEN = environ.get('BEARER_TOKEN')


class Twitter:
    def __init__(self) -> None:
        auth = tweepy.OAuth2BearerHandler(BEARER_TOKEN)
        self.api_v1_client = tweepy.API(auth)
        self.api_v2_client = tweepy.Client(BEARER_TOKEN)
        self.file_handler = FileHandler()

    def get_person_report(self, person_name: str) -> None:
        try:
            profile_info = self.get_profile_info(person_name)
        except NoTwitterProfileFound:
            return echo(f'No Twitter profile found for {person_name}.')

        last_tweets = self.get_last_tweets(profile_info.id)
        formatted_report = self.format_report(profile_info, last_tweets)
        self.file_handler.save_person_info(person_name, formatted_report, 'twitter')
        return echo(formatted_report)

    def get_profile_info(self, person_name: str) -> tweepy.User:
        echo(f'Getting profile info for {person_name}...')
        try:
            info_dict = self.api_v1_client.search_users(person_name)[0]
        except IndexError:
            raise NoTwitterProfileFound

        return info_dict

    def get_last_tweets(self, profile_id: str) -> List[tweepy.Tweet]:
        echo('Fetching recent tweets...')
        return self.api_v2_client.get_users_tweets(profile_id).data

    def format_report(self, profile_info: tweepy.User, last_tweets: List[tweepy.Tweet]) -> str:
        raise NotImplementedError
