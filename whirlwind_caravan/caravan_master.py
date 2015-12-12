import argparse
import datetime
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
            }
    requests.post(rest_url, json=data)


def store_packets(data, mongo_url):
    if data['count'] != 0:
        db = pymongo.MongoClient(mongo_url).sparkhara.count_packets
        db.insert_one(data)


def normalize_log_lines(log_lines, service_name=None):
    data = {'_id': None if len(log_lines) == 0 else uuid.uuid4().hex,
            'count': len(log_lines),
            'logs': log_lines,
            }
    return data


def process_generic(rdd, mongo_url, rest_url):
    log_lines = rdd.collect()
    print(log_lines)
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
    parser.add_argument('--port', help='the port to listen on',
                        default=9901, type=int)
    parser.add_argument('--appname', help='the name of the spark application',
                        default='SparkharaLogCounter')
    parser.add_argument('--master',
                        help='the master url for the spark cluster')
    args = parser.parse_args()
    mongo_url = args.mongo
    rest_url = args.rest

    sconf = SparkConf().setAppName(args.appname)
    if args.master:
        sconf.setMaster(args.master)
    sc = SparkContext(conf=sconf)
    ssc = StreamingContext(sc, 1)

    lines = ssc.socketTextStream('caravan-pathfinder', args.port)
    lines.foreachRDD(lambda rdd: process_generic(rdd, mongo_url, rest_url))

    ssc.start()
    ssc.awaitTermination()


if __name__ == '__main__':
    main()
