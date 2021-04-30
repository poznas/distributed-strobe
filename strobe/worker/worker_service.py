#!flask/bin/python
from flask import Flask, request, jsonify

from worker_heartbeat import start_heartbeat
from strobe_worker import StrobeWorker
from util.chrony import chronyc_tracking

worker = StrobeWorker()

app = Flask(__name__)


@app.route('/worker/sequence', methods=['PUT'])
def put_sequence():
    worker.set_sequence(request.get_json(force=True))
    return jsonify(success=True)


@app.route('/worker/execution', methods=['POST'], endpoint='start')
def register_execution():
    worker.register_tasks(float(request.args.get('start_time')))
    worker.start()
    return jsonify(success=True)


@app.route('/worker/execution', methods=['DELETE'], endpoint='stop')
def stop_execution():
    worker.stop()
    return jsonify(success=True)


@app.route('/worker/chrony/tracking', methods=['GET'])
def get_chrony_tracking():
    return jsonify(chronyc_tracking())


if __name__ == '__main__':
    start_heartbeat(StrobeWorker.worker_id())
    app.run(host='0.0.0.0')
