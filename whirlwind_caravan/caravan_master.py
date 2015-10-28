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
    error_lines = []
    nonerror_lines = []
    for l in log_lines:
        if 'Authorization failed' in l:
            error_lines.append(l)
        else:
            nonerror_lines.append(l)


    data = {'_id': None if len(nonerror_lines) == 0 else uuid.uuid4().hex,
            'count': len(nonerror_lines),
            'service': service_name,
            'errors': False,
            'logs': nonerror_lines,
            }
    error_data = {'_id': None if len(error_lines) == 0 else uuid.uuid4().hex,
            'count': len(error_lines),
            'service': 'errors',
            'errors': True,
            'logs': error_lines,
            }
    return data, error_data


def restore_newlines(loglines, separator='::newline::'):
    for i, line in enumerate(loglines):
        loglines[i] = line.replace(separator, '\n')


def process_generic(rdd, service_name):
    log_lines = rdd.collect()
    #restore_newlines(log_lines)
    data, error_data = normalize_log_lines(log_lines, service_name)
    data['processed-at'] = datetime.datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S.%f')[:-3]
    error_data['processed-at'] = data['processed-at']
    store_packets(data)
    signal_rest_server(data)
    if error_data['_id'] is not None:
        store_packets(error_data)
        signal_rest_server(error_data)


if __name__ == '__main__':
    sc = SparkContext(appName='SparkharaLogCounter')
    ssc = StreamingContext(sc, 1)

    sahara_lines = ssc.socketTextStream('127.0.0.1', 9901)
    sahara_lines.foreachRDD(lambda rdd: process_generic(rdd, 'keystone'))

    ssc.start()
    ssc.awaitTermination()
