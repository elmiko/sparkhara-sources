#!/bin/env python
'''
rock breaker

this application will send authentication requests to a keystone server.
it will send a mix of valid and invalid requests.

valid requests are sent once per second.

invalid requests are sent in groups of 1-10, every 3-7 seconds. both
sets of values being determined randomly.

'''
import argparse
import random
import threading
import time

import requests


good_req = {
    "auth": {
        "tenantName": "demo",
        "passwordCredentials": {
            "username": "demo",
            "password": "openstack"
            }
        }
    }

bad_req = {
    "auth": {
        "tenantName": "demo",
        "passwordCredentials": {
            "username": "demo",
            "password": "notmypassword"
            }
        }
    }


def good_guy(url):
    while True:
        resp = requests.post(url, json=good_req)
        print(resp)
        time.sleep(1)


def bad_guy(url):
    while True:
        for i in range(random.randint(1, 10)):
            resp = requests.post(url, json=bad_req)
            print(resp)
        time.sleep(random.randint(3, 7))


def main():
    parser = argparse.ArgumentParser(
        description='hammer a keystone server with auth requests')
    parser.add_argument('--url', help='the keystone url to hit',
                        required=True)
    args = parser.parse_args()

    if args.url.endswith('v2.0'):
        url = args.url + '/tokens'
    else:
        print('unrecognized keystone url')
        return

    good_th = threading.Thread(target=good_guy, args=(url,))
    good_th.start()

    bad_th = threading.Thread(target=bad_guy, args=(url,))
    bad_th.start()

if __name__ == '__main__':
    main()
