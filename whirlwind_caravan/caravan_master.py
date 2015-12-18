import argparse
import datetime
import json
import sys
import uuid

import pymongo
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import requests


def signal_rest_server(rawdata, rest_url):
    data = {'id': rawdata['_id'],
            'count': rawdata['count'],
            'service-counts': rawdata['service-counts'],
            }
    try:
        requests.post(rest_url, json=data)
    except Exception as ex:
        print('handled: {}'.format(ex))


def store_packets(rawdata, mongo_url):
    data = {'_id': rawdata['_id'],
            'processed-at': rawdata['processed-at'],
            'count': rawdata['count'],
            'log-ids': rawdata['log-ids'],
            }
    db = pymongo.MongoClient(mongo_url).sparkhara
    db.count_packets.insert_one(data)
    data = rawdata['log-packets']
    db.log_packets.insert_many(data, ordered=False)


def normalize_log_lines(log_lines, service_name=None):
    norm_log_lines = []
    service_counts = {}
    for line in log_lines:
        for k, v in json.loads(line).items():
            repack = {'_id': uuid.uuid4().hex,
                      'service': k,
                      'log': v,
                      }
            norm_log_lines.append(repack)
            service_counts[k] = service_counts.get(k, 0) + 1
    data = {'_id': uuid.uuid4().hex,
            'count': len(norm_log_lines),
            'log-ids': [l['_id'] for l in norm_log_lines],
            'log-packets': norm_log_lines,
            'service-counts': service_counts,
            }
    return data


def process_generic(rdd, mongo_url, rest_url):
    log_lines = rdd.collect()
    print(len(log_lines), "processed")
    if len(log_lines) > 0:
        data = normalize_log_lines(log_lines)
        data['processed-at'] = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S.%f')[:-3]
        store_packets(data, mongo_url)
        signal_rest_server(data, rest_url)


def main():
    parser = argparse.ArgumentParser(
        description='process some log messages, storing them and signaling '
                    'a rest server')
    parser.add_argument('--mongo', help='the mongodb url',
                        required=True)
    parser.add_argument('--rest', help='the rest endpoint to signal',
                        required=True)
    parser.add_argument('--port', help='the port to receive from',
                        default=1984, type=int)
    parser.add_argument('--appname', help='the name of the spark application',
                        default='SparkharaLogCounter')
    parser.add_argument('--master',
                        help='the master url for the spark cluster')
    parser.add_argument('--socket',
                        help='the socket to attach for streaming text data',
                        default='caravan-pathfinder')
    args = parser.parse_args()
    mongo_url = args.mongo
    rest_url = args.rest

    sconf = SparkConf().setAppName(args.appname)
    if args.master:
        sconf.setMaster(args.master)
    sc = SparkContext(conf=sconf)
    ssc = StreamingContext(sc, 1)

    lines = ssc.socketTextStream(args.socket, args.port)
    lines.foreachRDD(lambda rdd: process_generic(rdd, mongo_url, rest_url))

    ssc.start()
    ssc.awaitTermination()


if __name__ == '__main__':
    main()
