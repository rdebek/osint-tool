import click
from osint_tool.data_fetching.hibp import Hibp
from osint_tool.data_fetching.netcraft import Netcraft


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
