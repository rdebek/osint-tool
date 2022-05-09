from os import environ
from click import echo
import shodan


SHODAN_KEY = environ.get('SHODAN_KEY')


class Shodan:
    def __init__(self):
        self.api = shodan.Shodan(SHODAN_KEY)

    def get_report_by_ip(self, ip_address) -> None:
        echo('Fetching data from Shodan...\n')
        return_str = ''
        host = self.api.host(ip_address, minify=True)
        if host["os"]:
            return_str += f'Operating system: {host["os"]}\n'
        return_str += f'Latitude: {host["latitude"]}\nLongitude: {host["longitude"]}\nOpen ' \
                      f'ports: {host["ports"]}\nLast update: {host["last_update"]}\n'
        echo(return_str)
