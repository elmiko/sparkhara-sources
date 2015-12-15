import argparse
import copy
import datetime

import flask as f
import pymongo


app = f.Flask(__name__)

_mongourl = None

LOG_ALL = 'all'
LOG_UNKNOWN = 'unknown'


class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @property
    def initialized(self):
        return hasattr(self, '_initialized')

    @staticmethod
    def check_initialized(func):
        def wrapper(self, *args, **kwargs):
            if not self.initialized:
                retval = func(self, *args, **kwargs)
                self._initialized = True
                return retval
        return wrapper


class LogTotals(Singleton):
    class TotalCounter(object):
        def __init__(self, initial_value=0):
            self.value = initial_value
            self.last_value = initial_value

        def add(self, count):
            self.last_value = self.value
            self.value += int(count)

        def update(self, new_value):
            self.value = new_value

    @Singleton.check_initialized
    def __init__(self):
        self.log_totals = {
            LOG_ALL: LogTotals.TotalCounter(),
            LOG_UNKNOWN: LogTotals.TotalCounter(),
            }

    def get(self, log):
        return self.log_totals[log].value

    def to_dict(self):
        return {
            'totals': {k: int(v.value) for k, v in self.log_totals.items()}}

    def add(self, log, count):
        if log not in self.log_totals:
            self.log_totals[log] = LogTotals.TotalCounter()
        self.log_totals[log].add(count)
        if log != LOG_ALL:
            self.log_totals[LOG_ALL].add(count)

    def update_from_dict(self, new_totals):
        for k, v in self.log_totals.items():
            if k in new_totals:
                v.update(new_totals[k])


class CountPackets(Singleton):
    @Singleton.check_initialized
    def __init__(self):
        self.flush()
        self.last_packet = {
            'id': None,
            'count': 0
            }

    def flush(self):
        self.since_last_get = {
            'ids': [],
            'count': 0,
            'errors': False,
            'by-service': {},
            }

    def to_dict(self):
        return {
            'count-packets': {
                'last-received': copy.deepcopy(self.last_packet),
                'since-last-get': copy.deepcopy(self.since_last_get)
                }
            }

    def update_from_dict(self, new_packet):
        if new_packet['service'] not in self.since_last_get['by-service']:
            self.since_last_get['by-service'][new_packet['service']] = {
                    'ids': [],
                    'count': 0,
                    'errors': False,
                    }
        self.last_packet['id'] = new_packet.get('id')
        self.last_packet['count'] = int(new_packet.get('count', 0))
        self.since_last_get['count'] += int(new_packet.get('count', 0))
        self.since_last_get['by-service'][new_packet['service']]['count'] += int(new_packet.get('count', 0))
        if new_packet.get('id') is not None:
            self.since_last_get['ids'].append(new_packet.get('id'))
            self.since_last_get['by-service'][new_packet['service']]['ids'].append(
                new_packet.get('id'))
        if new_packet.get('errors') is True:
            self.since_last_get['errors'] = True
            self.since_last_get['by-service'][new_packet['service']]['errors'] = True


@app.route('/')
def index():
    return f.render_template('index.html')


@app.route('/count-packets', methods=['GET', 'POST'])
def count_packets():
    if f.request.method == 'POST':
        data = f.request.get_json()
        if not data:
            return f.jsonify(message='no data found'), 400
        print('received some data')
        print(data)
        data['service'] = data.get('service') or LOG_UNKNOWN
        CountPackets().update_from_dict(data)
        LogTotals().add(data.get('service'), data.get('count'))
        status = 201
        ret = ''
    else:
        status = 200
        ret = f.jsonify(CountPackets().to_dict())
        CountPackets().flush()
    return ret, status


@app.route('/count-packets/<packet_id>', methods=['GET'])
def packet_detail(packet_id):
    db = pymongo.MongoClient(_mongourl).sparkhara.count_packets
    packet = db.find_one(packet_id)
    if packet is None:
        return f.jsonify(message='packet not found'), 404
    ret = {'count-packet': {'id': packet_id, 'logs': packet.get('logs')}}
    return f.jsonify(ret)


@app.route('/sorted-logs')
def sorted_logs():
    ids = f.request.args.getlist('ids')
    print(ids)
    logs = []
    db = pymongo.MongoClient(_mongourl).sparkhara.count_packets
    for i in ids:
        packet = db.find_one(i)
        if packet:
            logs += packet.get('logs')

    def log_sort(a, b):
        print(a)
        print(b)
        try:
            date1 = datetime.datetime.strptime(a.split('::')[0],
                                               '%Y-%m-%d %H:%M:%S.%f')
            date2 = datetime.datetime.strptime(b.split('::')[0],
                                               '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            return 0
        return cmp(date1, date2)

    ret = {'sorted-logs': {'lines': sorted(logs, log_sort)}}
    return f.jsonify(ret), 200


@app.route('/totals')
def totals():
    return f.jsonify(LogTotals().to_dict())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='run the shiny squirrel server')
    parser.add_argument('--mongo', help='the mongodb url',
                        required=True)
    args = parser.parse_args()
    _mongourl = args.mongo
    print('MongoDB at {}'.format(_mongourl))

    app.debug = True
    app.run(host='0.0.0.0', port=9050)
