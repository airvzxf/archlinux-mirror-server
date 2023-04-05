#!/usr/bin/env python3
"""
Get the information about Arch Linux mirror tier 1.
"""
from http.client import HTTPSConnection
from json import dumps, loads

from bs4 import BeautifulSoup


def get_tier1_html() -> str:
    """
    Get the tier servers and their information.
    """
    tier1_connection = HTTPSConnection('archlinux.org')
    tier1_connection.request('GET', '/mirrors/tier/1/')
    tier1_response = tier1_connection.getresponse()
    tier1_data = tier1_response.read()
    tier1_data_decoded = tier1_data.decode('utf-8')
    tier1_connection.close()

    if tier1_response.status != 200 or tier1_response.reason != "OK" or len(tier1_data_decoded) == 0:
        return ''

    return tier1_data_decoded


def get_tier1_list(html: str) -> list[dict]:
    """
    Convert html string to dictionary.

    :type html: str
    :param html: HTML web page.
    """
    tier1_object = []

    parsed_html = BeautifulSoup(html, 'html.parser')
    div_mirror_list = parsed_html.find(id='dev-mirrorlist')
    if div_mirror_list is None:
        return tier1_object

    table = div_mirror_list.table.tbody
    if table is None:
        return tier1_object

    servers = table.find_all('tr')
    for server in servers:
        attributes = server.find_all('td')
        if attributes[3].string.strip() == 'NO':
            continue

        tier1_object.append({
            'domain': attributes[0].a.string.strip(),
            'country': attributes[1].get_text().strip(),
            'tier': attributes[2].string.strip(),
            'iso': attributes[3].string.strip(),
            'protocol': [x.strip() for x in attributes[4].string.split(',')],
        })

    return tier1_object


def convert_list_to_json(tier1: list[dict]) -> str:
    """
    Convert Python variable which is a list with dictionary to JSON.

    :type tier1: list[dict]
    :param tier1: A list with dictionaries.
    """

    return dumps(tier1)


def get_mirror_status_json() -> str:
    """
    Return the mirror status in JSON format.

    :rtype: str
    :return: Mirror status
    """
    tier1_connection = HTTPSConnection('archlinux.org')
    tier1_connection.request('GET', '/mirrors/status/json/')
    tier1_response = tier1_connection.getresponse()
    tier1_data = tier1_response.read()
    tier1_data_decoded = tier1_data.decode('utf-8')
    tier1_connection.close()

    return tier1_data_decoded


def extract_tier1_servers(mirrors: str, tier1: list[dict]) -> dict[str, list[dict]]:
    """
    Extract the tier 1 servers from the mirror status.

    :type mirrors: str
    :param mirrors: JSON string with all the status servers.

    :type tier1: list[dict]
    :param tier1: List of tier 1 servers.
    """
    tier1_urls = {
        'http': [],
        'https': [],
        'rsync': [],
    }

    for mirror in loads(mirrors)['urls']:
        for server_tier1 in tier1:
            if server_tier1['domain'].lower() in mirror['url'].lower():
                tier1_urls[mirror['protocol']].append(mirror)

    print(tier1_urls)
    print(dumps(tier1_urls))
    return tier1_urls


if __name__ == '__main__':
    servers_tier1_html = get_tier1_html()
    servers_tier1 = get_tier1_list(servers_tier1_html)
    # servers_tier1_json = convert_list_to_json(servers_tier1)

    mirror_status = get_mirror_status_json()
    final_tier1_info = extract_tier1_servers(mirror_status, servers_tier1)
