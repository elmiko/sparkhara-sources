import flask as f
import pymongo


app = f.Flask(__name__)

_logtotals=None
_countpackets=None

LOG_ALL='all'


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

    def update(self, new_value):
        self.last_value = self.value
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

    def update_from_dict(self, new_totals):
        for k, v in self.log_totals.items():
            if k in new_totals:
                v.update(new_totals[k])


class CountPackets(object):
    def __init__(self):
        self.last_packet = {
            'id': None,
            'count': 0
            }

    def to_dict(self):
        return { 'count-packets': {'last': self.last_packet}}

    def update_from_dict(self, new_packet):
        self.last_packet['id'] = new_packet.get('id')
        self.last_packet['count'] = int(new_packet.get('count', 0))


@app.route('/')
def index():
    return f.render_template('index.html')


@app.route('/totals', methods=['GET', 'POST'])
def totals():
    if f.request.method == 'POST':
        data = f.request.get_json()
        if not data:
            return f.jsonify(message='no data found'), 400
        logtotals().update_from_dict(data.get('totals'))
    return f.jsonify(logtotals().to_dict())


@app.route('/count-packets', methods=['GET', 'POST'])
def count_packets():
    if f.request.method == 'POST':
        data = f.request.get_json()
        if not data:
            return f.jsonify(message='no data found'), 400
        countpackets().update_from_dict(data)
    return f.jsonify(countpackets().to_dict())


@app.route('/count-packets/<packet_id>', methods=['GET'])
def packet_detail(packet_id):
    db = pymongo.MongoClient('10.0.1.107').sparkhara.count_packets
    packet = db.find_one(packet_id)
    if packet is None:
        return f.jsonify(message='packet not found'), 404
    ret = {'count-packet': {'logs': packet.get('logs')}}
    return f.jsonify(ret)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9050)
