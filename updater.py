#!/usr/bin/env python3
# Original Script by Michael Shepanski (2013-08-01, python 2)
# Updated to work with Python 3
# Updated to use DigitalOcean API v2

import argparse
import ipaddress
import json
import sys
import time
import urllib.request
import urllib.error
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
def put_url(url, data, headers):
    req = urllib.request.Request(url, data=data, headers=headers)
    req.get_method = lambda: 'PUT'
    with urllib.request.urlopen(req) as file:
        data = file.read()
        return data.decode('utf8')


def get_external_ip(expected_rtype):
    """ Return the current external IP. """
    external_ip = get_url(CHECKIP_URL).rstrip()
    ip = ipaddress.ip_address(external_ip)
    if (ip.version == 4 and expected_rtype != 'A') or (ip.version == 6 and expected_rtype != 'AAAA'):
        raise Exception("Expected Rtype {} but got {}".format(expected_rtype, external_ip))
    debug("Obtaining the current external IP address: {}", external_ip)
    return external_ip


def get_domain(name, token):
    debug("Fetching Domain ID for: {}", name)
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

    raise Exception(f"Could not find domain: {name}")


def get_record(domain, name, rtype, token):
    debug("Fetching Record ID for: {}", name)
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

    raise Exception(f"Could not find record: {name}")


def set_record_ip(domain, record, ipaddr, token):
    debug("Updating record {}.{} to {}", record['name'], domain['name'], ipaddr)

    url = "%s/domains/%s/records/%s" % (APIURL, domain['name'], record['id'])
    data = json.dumps({'data': ipaddr}).encode('utf-8')
    headers = create_headers(token, {'Content-Type': 'application/json'})

    result = json.loads(put_url(url, data, headers))
    if result['domain_record']['data'] == ipaddr:
        debug("Record {}.{} sucessfully updated to {}", record['name'], domain['name'], ipaddr)
    else:
        raise Exception(f"Could not set {record['name']}.{domain['name']} to {ipaddr}")


def output(line, *args):
    quiet = getattr(output, 'quiet', False)
    if quiet:
        return
    print(f"[{datetime.now()}]", line.format(*args))


def debug(line, *args):
    debug = getattr(debug, 'debug', False)
    if not debug:
        return
    output(f"DEBUG - {line}", *args)

def process_args():
    parser = argparse.ArgumentParser(description='Updates DNS records in Digital Ocean')
    parser.add_argument("token")
    parser.add_argument("domain")
    parser.add_argument("record")
    parser.add_argument("rtype", choices=['A', 'AAAA'])
    parser.add_argument("-q", "--quiet",
                        action="store_true",
                        help="Only display output on IP change")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Shows debug messages")
    parser.add_argument("-ecoc", "--error-code-on-change",
                        action="store_true",
                        help="Return Error Code 1 on IP change")
    parser.add_argument("-re", "--run-every",
                        help="Run every number of seconds")
    return parser.parse_args()


def run(args):
    try:
        debug("Update {}.{} record type {}", args.record, args.domain, args.rtype)
        ipaddr = get_external_ip(args.rtype)
        domain = get_domain(args.domain, args.token)
        record = get_record(domain, args.record, args.rtype, args.token)
        if record['data'] == ipaddr:
            output("Record {}.{} already set to {}", record['name'], domain['name'], ipaddr)
            return 0

        set_record_ip(domain, record, ipaddr, args.token)
        ec = 1 if args.error_code_on_change else 0
        return ec

    except (Exception) as err:
        print(f"[{datetime.now()}] ERROR - {err}", file=sys.stderr)
        return -1


if __name__ == '__main__':
    args = process_args()
    if args.debug:
        debug.debug = True

    if args.quiet:
        output.quiet = True

    if args.run_every:
        timeout = int(args.run_every)
        output("Running this script continuously every {} seconds", timeout)
        starttime=time.time()
        while True:
          run(args)
          time.sleep(timeout - ((time.time() - starttime) % timeout))
    else:
        sys.exit(run(args))
