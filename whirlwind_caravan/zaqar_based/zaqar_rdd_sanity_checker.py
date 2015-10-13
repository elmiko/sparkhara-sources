import threading
import time

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

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

def total_emitter(acc):
    client = get_client()
    queue = client.queue('log_totals')
    while True:
        time.sleep(5)
        queue.post({'body': acc.value, 'ttl': 300})

if __name__ == '__main__':
    sc = SparkContext(appName='SparkharaLogCounter')
    ssc = StreamingContext(sc, 1)

    total_lines = sc.accumulator(0)

    def rdd_print(rdd):
        a = rdd.collect()
        total_lines.add(len(a))

    lines = ssc.socketTextStream('0.0.0.0', 9901)
    lines.foreachRDD(rdd_print)

    th = threading.Thread(target=total_emitter, args=(total_lines,))
    th.start()
    ssc.start()
    ssc.awaitTermination()
