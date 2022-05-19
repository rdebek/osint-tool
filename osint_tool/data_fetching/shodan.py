import shodan
from click import echo

from osint_tool.util.credentials_manager import SHODAN_KEY
from osint_tool.util.file_handler import FileHandler


class Shodan:
    def __init__(self):
        self.api = shodan.Shodan(SHODAN_KEY)
        self.file_handler = FileHandler()

    def get_shodan_report(self, site_url: str, ip_address: str) -> None:
        echo('Fetching data from Shodan...\n')
        return_str = ''
        host = self.api.host(ip_address, minify=True)
        if host["os"]:
            return_str += f'Operating system: {host["os"]}\n'
        return_str += f'Latitude: {host["latitude"]}\nLongitude: {host["longitude"]}\nOpen ' \
                      f'ports: {host["ports"]}\nLast update: {host["last_update"]}\n'
        self.file_handler.save_site_info(site_url, return_str, 'shodan')
        echo(return_str)
