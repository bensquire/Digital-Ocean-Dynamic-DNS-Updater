#!/usr/bin/python
# Original Script by Michael Shepanski (2013-08-01, python 2)
# Updated to work with Python 3
# Updated to use Digital Oean API v2

import json, re
from datetime import datetime

# Support both v2 and v3 urllibs
try:
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError, ex:
    from urllib2 import urlopen
    from urllib2 import Request

TOKEN = ''     # Digital Ocean Personal Access Token (read & write)
DOMAIN = ''    # joebloggs.co.uk
RECORD = ''    # home

CHECKIP = "http://checkip.dyndns.org:8245/"
APIURL = "https://api.digitalocean.com/v2"
AUTH_HEADER = {'Authorization': "Bearer %s" % (TOKEN)}

def get_external_ip():
    """ Return the current external IP. """
    print ("Fetching external IP from:", CHECKIP)

    fp = urlopen(CHECKIP)
    mybytes = fp.read()
    html = mybytes.decode("utf8")

    external_ip = re.findall('[0-9.]+', html)[0]
    print ("Found external IP: ", external_ip)
    return external_ip

def get_domain(name=DOMAIN):
    print ("Fetching Domain ID for:", name)
    url = "%s/domains" % (APIURL)

    req = Request(url, headers=AUTH_HEADER)
    fp = urlopen(req)
    mybytes = fp.read()
    html = mybytes.decode("utf8")

    result = json.loads(html)

    for domain in result['domains']:
        if domain['name'] == name:
            return domain
    raise Exception("Could not find domain: %s" % name)

def get_record(domain, name=RECORD):
    print ("Fetching Record ID for: ", name)
    url = "%s/domains/%s/records" % (APIURL, domain['name'])

    req = Request(url, headers=AUTH_HEADER)
    fp = urlopen(req)
    mybytes = fp.read()
    html = mybytes.decode("utf8")
    result = json.loads(html)

    for record in result['domain_records']:
        if record['type'] == 'A' and record['name'] == name:
            return record
    raise Exception("Could not find record: %s" % name)

def set_record_ip(domain, record, ipaddr):
    print ("Updating record", record['name'], ".", domain['name'], "to", ipaddr)

    url = "%s/domains/%s/records/%s" % (APIURL, domain['name'], record['id'])
    data = json.dumps({'data' : ipaddr}).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    headers.update(AUTH_HEADER)

    req = Request(url, data, headers, method='PUT')
    fp = urlopen(req)
    mybytes = fp.read()
    html = mybytes.decode("utf8")
    result = json.loads(html)

    if result['domain_record']['data'] == ipaddr:
        print ("Success")


if __name__ == '__main__':
    try:
        print ("Updating ", RECORD, ".", DOMAIN, ":", datetime.now())
        ipaddr = get_external_ip()
        domain = get_domain()
        record = get_record(domain)
        if record['data'] == ipaddr:
            print ("Record %s.%s already set to %s." % (record['name'], domain['name'], ipaddr))
        else:
            set_record_ip(domain, record, ipaddr)
    except (Exception) as err:
        print ("Error: ", err)
