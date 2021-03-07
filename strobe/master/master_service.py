#!flask/bin/python
import sys

from datetime import datetime
from flask import Flask, request, jsonify, render_template

from strobe_master import StrobeMaster

master = None

app = Flask(__name__)


def _time(timestamp: float):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")


@app.route('/', methods=['GET'])
def master_ui():
    return render_template('index.html', slaves=master.slaves.items(), _time=_time)


@app.route('/master/slaves', methods=['PUT'])
def register_slave():
    master.register_slave(request.args.get('node_id'), request.remote_addr, request.get_json(force=True))
    return jsonify(success=True)


@app.route('/master/sequence/publish', methods=['POST'])
def register_execution():
    master.publish_offsets()
    return jsonify(success=True)


@app.route('/master/execution', methods=['POST'], endpoint='start')
def register_execution():
    master.register_tasks(float(request.args.get('start_time')))
    master.start()
    return jsonify(success=True)


@app.route('/master/execution', methods=['DELETE'], endpoint='stop')
def stop_execution():
    master.stop()
    return jsonify(success=True)


if __name__ == '__main__':
    master = StrobeMaster(sys.argv[1], sys.argv[2])

    app.run(host='0.0.0.0')
