#!flask/bin/python
import sys

from flask import Flask, request, jsonify

from strobe_master import StrobeMaster

master = None

app = Flask(__name__)


@app.route('/master/slaves', methods=['PUT'])
def register_slave():
    master.register_slave(request.args.get('node_id'), request.remote_addr)
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

    app.run(host='0.0.0.0', debug=True)
