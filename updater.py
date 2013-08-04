#!/usr/bin/python
# Original Script by Michael Shepanski (2013-08-01, python 2)
# Updated to work with Python 3

import json, re
import urllib.request
from datetime import datetime

CLIENTID = ''
APIKEY = ''
DOMAIN = ''
RECORD = ''

CHECKIP = "http://checkip.dyndns.org:8245/"
APIURL = "https://api.digitalocean.com"
APICREDS = "client_id=%s&api_key=%s" % (CLIENTID, APIKEY)


def get_external_ip():
    """ Return the current external IP. """
    print ("Fetching external IP from:", CHECKIP)

    fp = urllib.request.urlopen(CHECKIP)
    mybytes = fp.read()
    html = mybytes.decode("utf8")

    external_ip = re.findall('[0-9.]+', html)[0]
    print ("Found external IP: ", external_ip)
    return external_ip

def get_domain(name=DOMAIN):
    print ("Fetching Domain ID for:", name)
    url = "%s/domains?%s" % (APIURL, APICREDS)

    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    html = mybytes.decode("utf8")

    result = json.loads(html)

    for domain in result['domains']:
        if domain['name'] == name:
            return domain
    raise Exception("Could not find domain: %s" % name)

def get_record(domain, name=RECORD):
    print ("Fetching Record ID for: ", name)
    url = "%s/domains/%s/records?%s" % (APIURL, domain['id'], APICREDS)

    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    html = mybytes.decode("utf8")
    result = json.loads(html)

    for record in result['records']:
        if record['name'] == name:
            return record
    raise Exception("Could not find record: %s" % name)

def set_record_ip(domain, record, ipaddr):
    print ("Updating record", record['name'], ".", domain['name'], "to", ipaddr)

    url = "%s/domains/%s/records/%s/edit?%s&data=%s" % (APIURL, domain['id'], record['id'], APICREDS, ipaddr)
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    html = mybytes.decode("utf8")
    result = json.loads(html)

    if result['status'] == 'OK':
        print ("Success")


if __name__ == '__main__':
    try:
        print ("Updating ", RECORD, ".", DOMAIN, ":", datetime.now())
        ipaddr = get_external_ip()
        domain = get_domain()
        record = get_record(domain)
        if record['data'] == ipaddr:
            raise SystemExit("Record %s.%s already set to %s." % (record['name'], domain['name'], ipaddr))
        set_record_ip(domain, record, ipaddr)
    except (Exception) as err:
        print ("Error: ", err)
