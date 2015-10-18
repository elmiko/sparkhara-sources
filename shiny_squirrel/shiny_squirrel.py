import copy
import datetime

import flask as f
import pymongo


app = f.Flask(__name__)

_logtotals = None
_countpackets = None

LOG_ALL = 'all'


def logtotals():
    global _logtotals
    if _logtotals is None:
        _logtotals = LogTotals()
    return _logtotals


def countpackets():
    global _countpackets
    if _countpackets is None:
        _countpackets = CountPackets()
    return _countpackets


class TotalCounter(object):
    def __init__(self, initial_value=0):
        self.value = initial_value
        self.last_value = initial_value

    def add(self, count):
        self.last_value = self.value
        self.value += int(count)

    def update(self, new_value):
        self.value = new_value


class LogTotals(object):
    def __init__(self):
        self.log_totals = {
            LOG_ALL: TotalCounter(),
            }

    def get(self, log):
        return self.log_totals[log].value

    def to_dict(self):
        return {
            'totals': {k: int(v.value) for k, v in self.log_totals.items()}}

    def add(self, log, count):
        self.log_totals[log].add(count)

    def update_from_dict(self, new_totals):
        for k, v in self.log_totals.items():
            if k in new_totals:
                v.update(new_totals[k])


class CountPackets(object):
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
            }

    def to_dict(self):
        return {
            'count-packets': {
                'last-received': copy.deepcopy(self.last_packet),
                'since-last-get': copy.deepcopy(self.since_last_get)
                }
            }

    def update_from_dict(self, new_packet):
        self.last_packet['id'] = new_packet.get('id')
        self.last_packet['count'] = int(new_packet.get('count', 0))
        self.since_last_get['count'] += int(new_packet.get('count', 0))
        if new_packet.get('id') is not None:
            self.since_last_get['ids'].append(new_packet.get('id'))
        if new_packet.get('errors') is True:
            self.since_last_get['errors'] = True


@app.route('/')
def index():
    return f.render_template('index.html')


@app.route('/count-packets', methods=['GET', 'POST'])
def count_packets():
    if f.request.method == 'POST':
        data = f.request.get_json()
        if not data:
            return f.jsonify(message='no data found'), 400
        countpackets().update_from_dict(data)
        logtotals().add(LOG_ALL, data.get('count'))
        status = 201
        ret = ''
    else:
        status = 200
        ret = f.jsonify(countpackets().to_dict())
        countpackets().flush()
    return ret, status


@app.route('/count-packets/<packet_id>', methods=['GET'])
def packet_detail(packet_id):
    db = pymongo.MongoClient('10.0.1.107').sparkhara.count_packets
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
    db = pymongo.MongoClient('10.0.1.107').sparkhara.count_packets
    for i in ids:
        packet = db.find_one(i)
        if packet:
            logs += packet.get('logs')

    def log_sort(a, b):
        print(a)
        print(b)
        date1 = datetime.datetime.strptime(a.split('::')[0],
                                           '%Y-%m-%d %H:%M:%S.%f')
        date2 = datetime.datetime.strptime(b.split('::')[0],
                                           '%Y-%m-%d %H:%M:%S.%f')
        return cmp(date1, date2)

    ret = {'sorted-logs': {'lines': sorted(logs, log_sort)}}
    return f.jsonify(ret), 200


@app.route('/totals')
def totals():
    return f.jsonify(logtotals().to_dict())


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9050)
