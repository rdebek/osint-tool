import json

with open('secret.json', 'r') as j:
    credentials = json.loads(j.read())

LINKEDIN_LOGIN = credentials['LINKEDIN_LOGIN']
LINKEDIN_PASS = credentials['LINKEDIN_PASS']
BEARER_TOKEN = credentials['BEARER_TOKEN']
SHODAN_KEY = credentials['SHODAN_KEY']
