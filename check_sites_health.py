import os
import random
import argparse
import requests
import whois
from urllib.parse import urlparse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from constants import USER_AGENTS


def load_urls4check(urls_path):
    with open(urls_path, 'r') as urls_file:
        for line in urls_file:
            yield line.strip()


def is_server_response_ok(url, user_agents=None):
    headers = {}
    if user_agents:
        headers = {'User-Agent': random.choice(user_agents)}
    response = requests.head(
        url,
        headers=headers
    )
    return response.ok


def get_domain_expiration_date(url):
    domain_name = urlparse(url).netloc
    whois_response = whois.whois(domain_name)

    whois_expiration_date = whois_response.expiration_date
    if not whois_expiration_date:
        return

    if isinstance(whois_expiration_date, list):
        return whois_expiration_date[0]
    elif isinstance(whois_expiration_date, datetime):
        return whois_expiration_date


def get_domain_status(expiration_date, days_to_expire=30):
    today = datetime.now()
    if expiration_date is None:
        domain_status = None
    else:
        delta_days = expiration_date - today
        return delta_days >= timedelta(days=days_to_expire)


def check_statuses(url, user_agents=None):
    try:
        url_status = is_server_response_ok(url, user_agents)
    except requests.exceptions.ConnectionError:
        url_status = None

    expiration_date = get_domain_expiration_date(url)
    domain_status = get_domain_status(expiration_date)

    return url_status, domain_status


def get_urls_statuses(urls, user_agents=None):
    workers = os.cpu_count() * 2
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for url in urls:
            future = executor.submit(check_statuses, url, user_agents)
            futures[future] = url

        for future in as_completed(futures):
            url = futures[future]
            statuses = future.result()
            yield url, statuses


def is_filepath(path):
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(
            'It should be path to text file with urls list.'
        )
    return path


def get_args():
    parser = argparse.ArgumentParser(
        description='Tool for checking urls status'
    )
    parser.add_argument(
        '-p', '--urls-path',
        help='Path to file with urls',
        dest='urls_path',
        type=is_filepath
    )
    return parser.parse_args()


def print_statuses(statuses):
    print('Checked URLs:')
    horizontal_line = '-' * 105
    print(horizontal_line)
    row_template = '{:<60} | {:^20} | {:^20}'
    print(row_template.format('Url', 'Is URL ok', 'Domain status'))
    print(horizontal_line)

    for url, (url_status, domain_status) in statuses:
        print(
            row_template.format(
                url,
                'yes' if url_status else 'no',
                'error' if domain_status is None
                else 'OK' if domain_status else 'expired'
            )
        )


if __name__ == '__main__':
    args = get_args()

    urls = load_urls4check(args.urls_path)

    urls_statuses = get_urls_statuses(urls, USER_AGENTS)

    print_statuses(urls_statuses)
