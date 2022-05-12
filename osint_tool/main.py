import click
from osint_tool.data_fetching.hibp import Hibp
from osint_tool.data_fetching.netcraft import Netcraft
from osint_tool.data_fetching.shodan import Shodan
from osint_tool.data_fetching.linkedin import Linkedin


@click.command()
@click.argument('email')
def pwn_check(email):
    click.echo('Looking for data leaks...')
    pwnage_info = Hibp().check_if_pwned(email)
    click.echo(pwnage_info)


@click.command()
@click.argument('url')
def site_report(url):
    netcraft = Netcraft(url)
    click.echo('Checking page info...')
    netcraft.get_subdomains()
    netcraft.get_site_report()
    netcraft.get_site_technologies()
    shodan = Shodan()
    shodan.get_report_by_ip(netcraft.get_ip_from_url())


@click.command()
@click.argument('person')
def person_report(person):
    click.echo('Performing Linkedin lookup...')
    Linkedin().get_person_report(person)
