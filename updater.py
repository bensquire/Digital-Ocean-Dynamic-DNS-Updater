#!/usr/bin/python3
# Original Script by Michael Shepanski (2013-08-01, python 2)
# Updated to work with Python 3
# Updated to use DigitalOcean API v2

import argparse
import ipaddress
import json
import sys
import urllib.request
from datetime import datetime

# Parse the command line arguments (all required or else exception will be thrown)
parser = argparse.ArgumentParser()
parser.add_argument("token")
parser.add_argument("domain")
parser.add_argument("record")
parser.add_argument("rtype", choices=['A', 'AAAA'])
args = parser.parse_args()

# assign the parsed args to their respective variables
TOKEN = args.token
DOMAIN = args.domain
RECORD = args.record
RTYPE = args.rtype

CHECKIP_URL = "http://ipinfo.io/ip"
APIURL = "https://api.digitalocean.com/v2"
AUTH_HEADER = {'Authorization': "Bearer %s" % (TOKEN)}


def get_url(url, headers=None):
    if headers:
        req = urllib.request.Request(url, headers=headers)
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as file:
        data = file.read()
        return data.decode('utf8')


def get_external_ip():
    """ Return the current external IP. """
    external_ip = get_url(CHECKIP_URL).rstrip()
    ip = ipaddress.ip_address(external_ip)
    if (ip.version == 4 and RTYPE != 'A') or (ip.version == 6 and RTYPE != 'AAAA'):
        raise Exception('Expected Rtype {} but got {}'.format(RTYPE, external_ip))
    return external_ip


def get_domain(name=DOMAIN):
    print("Fetching Domain ID for:", name)
    url = "%s/domains" % (APIURL)

    while True:
        result = json.loads(get_url(url, headers=AUTH_HEADER))

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

    raise Exception("Could not find domain: %s" % name)


def get_record(domain, name=RECORD):
    print("Fetching Record ID for: ", name)
    url = "%s/domains/%s/records" % (APIURL, domain['name'])

    while True:
        result = json.loads(get_url(url, headers=AUTH_HEADER))

        for record in result['domain_records']:
            if record['type'] == RTYPE and record['name'] == name:
                return record

        if 'pages' in result['links'] and 'next' in result['links']['pages']:
            url = result['links']['pages']['next']
            # Replace http to https.
            # DigitalOcean forces https request, but links are returned as http
            url = url.replace("http://", "https://")
        else:
            break

    raise Exception("Could not find record: %s" % name)


def set_record_ip(domain, record, ipaddr):
    print("Updating record", record['name'], ".", domain['name'], "to", ipaddr)

    url = "%s/domains/%s/records/%s" % (APIURL, domain['name'], record['id'])
    data = json.dumps({'data': ipaddr}).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    headers.update(AUTH_HEADER)

    req = urllib.request.Request(url, data, headers, method='PUT')
    fp = urllib.request.urlopen(req)
    mybytes = fp.read()
    html = mybytes.decode("utf8")
    result = json.loads(html)

    if result['domain_record']['data'] == ipaddr:
        print("Success")


def run():
    try:
        print("Updating ", RECORD, ".", DOMAIN, ":", datetime.now())
        ipaddr = get_external_ip()
        domain = get_domain()
        record = get_record(domain)
        if record['data'] == ipaddr:
            print("Record %s.%s already set to %s." % (record['name'], domain['name'], ipaddr))
        else:
            set_record_ip(domain, record, ipaddr)
    except (Exception) as err:
        print("Error: ", err)


if __name__ == '__main__':
    sys.exit(run())
