from os import environ
from typing import List, Union

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

        if last_tweets:
            last_tweets_info = self.get_tweets_info([tweet.id for tweet in last_tweets])
            formatted_report = self.format_report(profile_info, last_tweets_info)
        else:
            formatted_report = self.format_report(profile_info)

        self.file_handler.save_person_info(person_name, formatted_report, 'twitter')
        return echo(formatted_report)

    def get_profile_info(self, person_name: str) -> tweepy.User:
        echo(f'Getting profile info for {person_name}...')
        try:
            info_dict = self.api_v1_client.search_users(person_name)[0]
        except IndexError:
            raise NoTwitterProfileFound from IndexError

        return info_dict

    def get_last_tweets(self, profile_id: str) -> Union[List[tweepy.Tweet], None]:
        echo('Fetching recent tweets...')
        tweets_found = self.api_v2_client.get_users_tweets(profile_id, exclude=['retweets', 'replies']).data
        if not tweets_found:
            return echo('No tweets found.')

        return tweets_found

    def get_tweets_info(self, tweet_ids: List[str]) -> List:
        tweets_info_array = []
        for tweet_id in tweet_ids:
            tweets_info_array.append(
                self.api_v1_client.get_status(tweet_id, include_entities=False, trim_user=True, tweet_mode="extended"))
        return tweets_info_array

    def format_report(self, profile_info: tweepy.User, last_tweets_info: List = None) -> str:
        basic_info = f'\n{self.validate_field(profile_info.name.upper())}\n'
        basic_info += f'Description: {self.validate_field(profile_info.description)}\n' \
                      f'Profile picture: {self.validate_field(profile_info.profile_image_url_https)}\n' \
                      f'Follow count: {self.validate_field(profile_info.followers_count)}\n' \
                      f'Account created at: {self.validate_field(profile_info.created_at)}\n' \
                      f'Number of tweets: {self.validate_field(profile_info.statuses_count)}\n' \
                      f'Location: {self.validate_field(profile_info.location)}\n'

        if not last_tweets_info:
            return basic_info

        tweets_info = '\nRECENT TWEETS\n\n'

        for tweet in last_tweets_info:

            tweet_content = tweet.full_text.replace('\n', '')

            tweets_info += f'Tweeted at: {tweet.created_at}\n' \
                           f'Content: {tweet_content}\n' \
                           f'Posted from: {tweet.source}\n' \
                           f'Likes: {tweet.favorite_count}\n' \
                           f'Retweets: {tweet.retweet_count}\n' \
                           f'Tweet language: {tweet.lang}\n'

            if not tweet.geo and not tweet.coordinates and not tweet.place:
                tweets_info += 'Location information: unknown \n\n'
            else:
                tweets_info += f'Location information: {tweet.geo, tweet.coordinates, tweet.place}\n\n'

        return basic_info + tweets_info

    @staticmethod
    def validate_field(field: str) -> str:
        return field if field else '---'
