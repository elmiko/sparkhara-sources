import datetime
import uuid

import pymongo
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import requests


def signal_rest_server(rawdata):
    data = {'id': rawdata['_id'],
            'count': rawdata['count'],
            'errors': rawdata['errors'],
            'service': rawdata['service'],
            }
    requests.post('http://localhost:9050/count-packets', json=data)


def store_packets(data):
    if data['count'] != 0:
        db = pymongo.MongoClient().sparkhara.count_packets
        db.insert_one(data)


def normalize_log_lines(log_lines, service_name=None):
    contains_error = False
    for l in log_lines:
        try:
            sl = l.split('::')
            if 'ERROR' in sl[2]:
                contains_error = True
        except IndexError:
            pass
    data = {'_id': None if len(log_lines) == 0 else uuid.uuid4().hex,
            'count': len(log_lines),
            'service': service_name,
            'errors': contains_error,
            'logs': log_lines,
            }
    return data


def restore_newlines(loglines, separator='::newline::'):
    for i, line in enumerate(loglines):
        loglines[i] = line.replace(separator, '\n')


def process_generic(rdd, service_name):
    log_lines = rdd.collect()
    restore_newlines(log_lines)
    data = normalize_log_lines(log_lines, service_name)
    data['processed-at'] = datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S.%f')[:-3]
    store_packets(data)
    signal_rest_server(data)


if __name__ == '__main__':
    sc = SparkContext(appName='SparkharaLogCounter')
    ssc = StreamingContext(sc, 1)

    sahara_lines = ssc.socketTextStream('127.0.0.1', 9901)
    sahara_lines.foreachRDD(lambda rdd: process_generic(rdd, 'sahara'))

    neutron_lines = ssc.socketTextStream('127.0.0.1', 9902)
    neutron_lines.foreachRDD(lambda rdd: process_generic(rdd, 'neutron'))

    nova_lines = ssc.socketTextStream('127.0.0.1', 9903)
    nova_lines.foreachRDD(lambda rdd: process_generic(rdd, 'nova'))

    ssc.start()
    ssc.awaitTermination()
