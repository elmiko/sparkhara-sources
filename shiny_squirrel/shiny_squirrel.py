import flask as f


app = f.Flask(__name__)

_logtotals=None

LOG_ALL='all'


def logtotals():
    global _logtotals
    if _logtotals is None:
       _logtotals = LogTotals()
    return _logtotals


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


if __name__ == '__main__':
    app.debug = True
    app.run()
