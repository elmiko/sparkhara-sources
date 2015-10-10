import time

from zaqarclient.queues import client as zaqarclient

conf = {
        'auth_opts': {
            'backend': 'keystone',
            'options': {
                'os_username': 'demo',
                'os_password': 'openstack',
                'os_project_name': 'demo',
                'os_auth_url': 'http://10.0.1.107:5000/v2.0/',
                }
            }
        }

ZAQAR_URL='http://10.0.1.107:8888/'
ZAQAR_VERSION=1.1

def get_client():
    return zaqarclient.Client(ZAQAR_URL, ZAQAR_VERSION, conf=conf)

def main():
    client = get_client()
    queue = client.queue('log_totals')
    while True:
        time.sleep(2)
        for msg in queue.pop(count=10):
            print(msg.body)
