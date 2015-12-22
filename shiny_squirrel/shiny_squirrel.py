import argparse
import collections
import copy
import datetime
import threading
import time

import flask as f
from flask import views
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
        self.history = collections.deque(maxlen=60)
        self.history_lock = threading.Lock()
        self.flush()
        self.last_packet = {
            'id': None,
            'count': 0,
            'service-counts': {},
            }

    def flush(self):
        self.since_last_update = {
            'ids': [],
            'count': 0,
            'service-counts': {},
            }

    def to_dict(self):
        return {
            'count-packets': {
                'last-received': copy.deepcopy(self.last_packet),
                'history': copy.deepcopy([i for i in self.history])
                }
            }

    def update_from_dict(self, new_packet):
        ''' update the count packets

        expecting something like this:

        {
          'id': '<id of the packet>',
          'count': int(<number of lines in this packet>),
          'service-counts': { '<service>': int(<count of lines>) }
        }

        '''
        if new_packet.get('id') is None:
            raise Exception('count packet contains no id')

        self.last_packet['id'] = new_packet['id']
        self.last_packet['count'] = int(new_packet.get('count', 0))
        self.last_packet['service-counts'] = copy.deepcopy(
            new_packet.get('service-counts', {}))

        self.since_last_update['ids'].append(self.last_packet['id'])
        self.since_last_update['count'] += self.last_packet['count']
        for service, count in self.last_packet['service-counts'].items():
            self.since_last_update['service-counts'][service] = (
                self.since_last_update['service-counts'].get(service, 0)
                + int(count))

    def update_history(self):
        self.history_lock.acquire()
        self.history.append(copy.deepcopy(self.since_last_update))
        self.flush()
        self.history_lock.release()


class CountPacketsTimer(threading.Thread):
    def __init__(self, counter, seconds, *args, **kwargs):
        super(CountPacketsTimer, self).__init__(*args, **kwargs)
        self.daemon = True
        self.counter = counter
        self.seconds = seconds

    def run(self):
        while True:
            self.counter.update_history()
            time.sleep(self.seconds)


class IndexView(views.MethodView):
    def get(self):
        return f.render_template('index.html')


class CountPacketsView(views.MethodView):
    def get(self):
        status = 200
        ret = f.jsonify(CountPackets().to_dict())
        return ret, status

    def post(self):
        data = f.request.get_json()
        if not data:
            return f.jsonify(message='no data found'), 400
        print('received some data')
        print(data)
        CountPackets().update_from_dict(data)
        status = 201
        ret = ''
        return ret, status


class SortedLogsView(views.MethodView):
    def get(self):
        ids = f.request.args.getlist('ids')
        print(ids)
        logs = []
        db = pymongo.MongoClient(_mongourl).sparkhara
        for i in ids:
            for log in db.log_packets.find({'count-packet': i}):
                logs.append(log['log'])

        def log_sort(a, b):
            print(a)
            print(b)
            try:
                date1 = datetime.datetime.strptime(
                    a.split('::')[0], '%Y-%m-%d %H:%M:%S.%f')
                date2 = datetime.datetime.strptime(
                    b.split('::')[0], '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                return 0
            return cmp(date1, date2)

        ret = {'sorted-logs': {'lines': sorted(logs, log_sort)}}
        return f.jsonify(ret), 200


class LogTotalsView(views.MethodView):
    def get(self):
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
    app.add_url_rule('/', view_func=IndexView.as_view('index'))
    app.add_url_rule('/totals', view_func=LogTotalsView.as_view('totals'))
    app.add_url_rule('/count-packets',
                     view_func=CountPacketsView.as_view('countpackets'))
    app.add_url_rule('/sorted-logs',
                     view_func=SortedLogsView.as_view('sortedlogs'))

    CountPacketsTimer(CountPackets(), 1).start()
    app.run(host='0.0.0.0', port=9050)
