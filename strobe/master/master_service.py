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
                           workers=master.workers.items(),
                           available_sequences=master.available_sequences,
                           active_sequence=master.active_sequence,
                           _time=_time)


@app.route('/master/workers/<worker_id>', methods=['GET'])
def worker_details_ui(worker_id):
    return render_template('worker_details.html', worker=master.workers[worker_id])


@app.route('/master/workers', methods=['PUT'])
def register_worker():
    master.register_worker(request.args.get('node_id'), request.remote_addr, request.get_json(force=True))
    return jsonify(success=True)


@app.route('/master/sequence/set-sequence', methods=['POST'])
def set_sequence():
    master.set_active_sequence(request.form['active_sequence'])
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
    sequence_dir = sys.argv[1] if len(sys.argv) > 1 else '../../sequence/test_sources'
    master = StrobeMaster(sequence_dir)

    app.run(host='0.0.0.0')
