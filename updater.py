#!/usr/bin/env python3
# Original Script by Michael Shepanski (2013-08-01, python 2)
# Updated to work with Python 3
# Updated to use DigitalOcean API v2

import argparse
import ipaddress
import json
import sys
import time
import os
import urllib.request
import urllib.error
import logging
import copy
import socket
import struct
from datetime import datetime
from functools import wraps

CHECKIP_URL = "http://ipinfo.io/ip"
APIURL = "https://api.digitalocean.com/v2"


def retry(times=-1, delay=0.5, errors=(Exception,)):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            count = 0
            while True:
                try:
                    count = count + 1
                    return f(*args, **kwargs)
                except errors as e:
                    if count == times:
                        raise e
                    time.sleep(delay)
        return wrapper
    return decorator


def create_headers(token, extra_headers=None):
    rv = {'Authorization': "Bearer %s" % (token)}
    if extra_headers:
        rv.update(extra_headers)
    return rv


@retry(times=5, delay=1.0, errors=(urllib.error.HTTPError,))
def get_url(url, headers=None):
    if headers:
        req = urllib.request.Request(url, headers=headers)
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as file:
        data = file.read()
        return data.decode('utf8')


@retry(times=5, delay=1.0, errors=(urllib.error.HTTPError,))
def request(url, data, headers, method=None):
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=os.environ.get('HTTP_TIMEOUT', 10)) as file:
        data = file.read()
        return data.decode('utf8')


def get_external_ip(expected_rtype):
    """ Return the current external IP. """
    external_ip = get_url(CHECKIP_URL).rstrip()
    ip = ipaddress.ip_address(external_ip)
    if (ip.version == 4 and expected_rtype != 'A') or (ip.version == 6 and expected_rtype != 'AAAA'):
        raise Exception('Expected Rtype {} but got {}'.format(expected_rtype, external_ip))
    return external_ip


class NoDomain(Exception):
    pass


class NoRecord(Exception):
    pass


def get_domain(name, token):
    logging.info('Fetching Domain ID for: %s', name)
    url = "%s/domains" % (APIURL)

    while True:
        result = json.loads(get_url(url, headers=create_headers(token)))

        for domain in result['domains']:
            if domain['name'] == name:
                return domain

        if 'pages' in result['links'] and 'next' in result['links']['pages']:
            url = result['links']['pages']['next']
            # Replace http to https.
            # DigitalOcean forces https request, but links are returned as http
            url = url.replace("http://", "https://")
        else:
            break

    raise NoDomain("Could not find domain: %s" % name)


def get_record(domain, name, rtype, token):
    logging.info("Fetching Record ID for: %s", name)
    url = "%s/domains/%s/records" % (APIURL, domain['name'])

    while True:
        result = json.loads(get_url(url, headers=create_headers(token)))

        for record in result['domain_records']:
            if record['type'] == rtype and record['name'] == name:
                return record

        if 'pages' in result['links'] and 'next' in result['links']['pages']:
            url = result['links']['pages']['next']
            # Replace http to https.
            # DigitalOcean forces https request, but links are returned as http
            url = url.replace("http://", "https://")
        else:
            break

    raise NoRecord("Could not find record: %s" % name)


def set_record_ip(domain, record, ipaddr, token):
    logging.info("Updating record %s.%s to %s", record['name'], domain['name'], ipaddr)

    url = "%s/domains/%s/records/%s" % (APIURL, domain['name'], record['id'])
    data = json.dumps({'data': ipaddr}).encode('utf-8')
    headers = create_headers(token, {'Content-Type': 'application/json'})

    result = json.loads(request(url, data, headers, 'PUT'))
    if result['domain_record']['data'] == ipaddr:
        logging.info("Success")


def create_record(domain, record, token):
    logging.info("Creating record %s.%s with value %s", record['name'], domain['name'], record['data'])
    logging.info(record)
    url = "%s/domains/%s/records" % (APIURL, domain['name'])
    assert 'name' in record
    assert 'type' in record
    assert 'data' in record
    data = json.dumps(record).encode('utf-8')
    headers = create_headers(token, {'Content-Type': 'application/json'})
    request(url, data, headers, 'POST')


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode())
    )[20:24])


def is_wireless(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        res = fcntl.ioctl(s.fileno(), 0x8B01, struct.pack('256s', ifname[:15].encode()))
        return True
    except OSError as e:
        return False


def get_ifaces():
    return os.listdir('/sys/class/net/')


def get_local_internet_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        print(s.getsockname())
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_fqdn(host, domain):
    return "{}.{}".format(host.rstrip('.'), domain)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", type=str, default=os.environ.get('DIGITAL_OCEAN_TOKEN'))
    parser.add_argument("-l", "--local", action='store_true',
                        help="Use the local ip connected to the internet")
    parser.add_argument("--rtype", choices=['A', 'AAAA'], default='A')
    parser.add_argument("record", type=str)
    parser.add_argument("domain", type=str)
    parser.add_argument("--ip", type=str, help='data field for the record such as ipv4 address, defaults to external ip if not set or local ip if --local given')
    parser.add_argument("--ttl", default='60', type=str)
    parser.add_argument("-q", "--quiet", action="store_true", help='Only display output on IP change')
    return parser.parse_args()


def script_name() -> str:
    """:returns: script name with leading paths removed"""
    return os.path.split(sys.argv[0])[1]


def config_logging():
    import time
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(format='{}: %(asctime)sZ %(levelname)s %(message)s'.format(script_name()))
    logging.Formatter.converter = time.gmtime


def main():
    config_logging()
    try:
        args = parse_args()
        if args.quiet:
            logging.disable(logging.INFO)

        if args.ip:
            ipaddr = args.ip
        elif args.local:
            ipaddr = get_local_internet_ip()
        else:
            ipaddr = get_external_ip(args.rtype)
            logging.info("Detected external ip address: %s", ipaddr)

        fqdn = get_fqdn(args.record, args.domain)
        logging.info("fqdn: %s", fqdn)
        try:
            resolved_ip = socket.gethostbyname(fqdn)
            if ipaddr == resolved_ip:
                logging.info("%s resolves to %s, up to date and no update required.", fqdn, resolved_ip)
                return 0
        except socket.gaierror as e:
            logging.exception(e)

        logging.info("Update %s %s.%s %s %s", args.rtype, args.record, args.domain, ipaddr, args.ttl)
        domain = get_domain(args.domain, args.token)
        action = None
        try:
            record = get_record(domain, args.record, args.rtype, args.token)
            if record['data'] == ipaddr:
                logging.info("Records %s.%s already set to %s.", record['name'], domain['name'], ipaddr)
                logging.info(record)
                return 0
            action = 'update'
        except NoRecord as e:
            action = 'create'
        if action == 'create':
            logging.warning("Record doesn't exist, creating...")
            record = dict(data=ipaddr, name=args.record, type=args.rtype, ttl=args.ttl)
            create_record(domain, record, args.token)
        else:
            assert action == 'update'
            logging.warning("Updating record from %s to %s", record['data'], ipaddr)
            set_record_ip(domain, record, ipaddr, args.token)
        return 0

    except Exception as e:
        logging.exception(e)
        return 1


if __name__ == '__main__':
    sys.exit(main())
