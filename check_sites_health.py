import os
import random
import argparse
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import whois

from constants import USER_AGENTS


def load_urls4check(urls_path):
    with open(urls_path, 'r') as urls_file:
        for line in urls_file:
            yield line.strip()


def is_server_respond_with_200(url, user_agents=None):
    if user_agents:
        user_agent = random.choice(user_agents)
    else:
        user_agent = 'python-requests/1.2.0'
    response = requests.head(
        url,
        headers={'User-Agent': user_agent}
    )
    return response.ok


def get_domain_expiration_date(url):
    domain_name = urlparse(url).netloc
    whois_response = whois.query(domain_name)
    expiration_date = whois_response.expiration_date
    today = datetime.now()
    delta_days = expiration_date - today
    return bool(delta_days >= timedelta(days=30))


def check_statuses(url, user_agents=None):
    try:
        url_status = is_server_respond_with_200(url, user_agents)
    except requests.exceptions.ConnectionError:
        url_status = False

    try:
        domain_status = get_domain_expiration_date(url)
    except:
        domain_status = False

    return url_status, domain_status


def get_urls_statuses(urls, user_agents=None):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(check_statuses, url, user_agents): url for url in urls
        }
        for future in as_completed(futures):
            url = futures[future]
            statuses = future.result()
            if not all(statuses):
                yield url, statuses


def is_filepath(path):
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(
            'It should be path to text file with urls list.'
        )
    return path


def get_args():
    parser = argparse.ArgumentParser(
        description='Tool for monitoring domains'
    )
    parser.add_argument(
        '-p', '--urls-path',
        help='Path to file with urls',
        dest='urls_path',
        type=is_filepath
    )
    return parser.parse_args()


def print_statuses(statuses):

    if not statuses:
        print('Everything is OK with your urls!')

    print('Urls that need your attention:')
    print('-' * 95)
    row_template = '{:<60} | {:^10} | {:^10}'
    print(row_template.format('Url', 'Is 200 OK', 'Is domain expired'))
    print('-' * 95)
    for url, (url_status, domain_status) in statuses:
        print(
            row_template.format(
                url,
                'yes' if url_status else 'no',
                'no' if domain_status else 'yes'
            )
        )


if __name__ == '__main__':
    args = get_args()

    urls = load_urls4check(args.urls_path)

    urls_statuses = get_urls_statuses(urls, USER_AGENTS)

    print_statuses(urls_statuses)
