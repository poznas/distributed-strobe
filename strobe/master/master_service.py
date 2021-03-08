#!flask/bin/python
import sys

from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, abort

from strobe_master import StrobeMaster

master = None

app = Flask(__name__)


def _time(timestamp: float):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")


@app.route('/', methods=['GET'])
def master_ui():
    return render_template('index.html',
                           slaves=master.slaves.items(),
                           active_sequence=master.active_sequence,
                           _time=_time)


@app.route('/master/slaves/<slave_id>', methods=['GET'])
def slave_details_ui(slave_id):
    return render_template('slave_details.html', slave=master.slaves[slave_id])


@app.route('/master/slaves', methods=['PUT'])
def register_slave():
    master.register_slave(request.args.get('node_id'), request.remote_addr, request.get_json(force=True))
    return jsonify(success=True)


@app.route('/master/sequence/publish', methods=['POST'])
def publish_offsets():
    master.publish_offsets()
    return redirect('/')


@app.route('/master/execution/start', methods=['POST'], endpoint='start')
def register_execution():
    try:
        master.register_execution(request.form.get('seconds_from_now'), request.form.get('start_at'))
    except ValueError as err:
        abort(400, err)
    master.start()
    return redirect('/')


@app.route('/master/execution/stop', methods=['POST'], endpoint='stop')
def stop_execution():
    master.stop()
    return redirect('/')


if __name__ == '__main__':
    master = StrobeMaster(sys.argv[1], sys.argv[2])

    app.run(host='0.0.0.0')
