import click
from osint_tool.data_fetching.hibp import Hibp


@click.command()
@click.argument('email')
def pwn_check(email):
    click.echo('Looking for data leaks...')
    pwnage_info = Hibp().check_if_pwned(email)
    click.echo(pwnage_info)
