import click

from osint_tool.data_fetching.google import Google
from osint_tool.data_fetching.linkedin import Linkedin
from osint_tool.data_fetching.netcraft import Netcraft
from osint_tool.data_fetching.shodan import Shodan
from osint_tool.data_fetching.twitter import Twitter
from osint_tool.data_fetching.whatsmyip import Whatsmyip


@click.command()
@click.argument('email')
def pwn_check(email):
    click.echo('Looking for data leaks...')
    pwnage_info = Whatsmyip(email).check_if_pwned()
    click.echo(pwnage_info)


@click.command()
@click.argument('url')
def site_report(url):
    click.echo('Checking page info...')
    netcraft = Netcraft(url)
    netcraft.get_site_report()
    Shodan().get_shodan_report(url, netcraft.get_ip_address())


@click.command()
@click.argument('person')
def person_report(person):
    click.echo('Performing Linkedin lookup...')
    Linkedin().get_person_report(person)
    click.echo('\n\nPerforming Twitter lookup...')
    Twitter().get_person_report(person)


@click.command()
@click.argument('mail_domain')
def gather_emails(mail_domain):
    click.echo(f'Gathering emails from @{mail_domain}...')
    click.echo(Google().get_emails(mail_domain))
    # Google().get_person_email('andrzej kowalski')
    # Google().get_person_number()


@click.command()
@click.argument('prefix')
def gather_numbers(prefix):
    click.echo(f'Gathering phone numbers with +{prefix} prefix...')
    Google().get_phone_numbers(prefix)
