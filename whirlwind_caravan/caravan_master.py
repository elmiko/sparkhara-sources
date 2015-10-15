import time
import uuid

import pymongo
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import requests


def signal_rest_server(rawdata):
    data = {'id': rawdata['_id'],
            'count': rawdata['count'],
            }
    requests.post('http://10.0.1.107:9050/count-packets', json=data)


def store_log_packets(rdd):
    log_lines = rdd.collect()
    data = {'_id': None if len(log_lines) == 0 else uuid.uuid4().hex,
            'count': len(log_lines),
            'logs': log_lines,
            }
    if len(log_lines) != 0:
        db = pymongo.MongoClient('10.0.1.107').sparkhara.count_packets
        db.insert_one(data)
    signal_rest_server(data)


if __name__ == '__main__':
    sc = SparkContext(appName='SparkharaLogCounter')
    ssc = StreamingContext(sc, 1)

    lines = ssc.socketTextStream('0.0.0.0', 9901)
    lines.foreachRDD(store_log_packets)

    ssc.start()
    ssc.awaitTermination()
