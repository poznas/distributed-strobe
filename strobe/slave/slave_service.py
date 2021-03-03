#!flask/bin/python
from flask import Flask, request, jsonify

from strobe_slave import StrobeSlave
from util.chrony import chronyc_tracking

slave = StrobeSlave()

app = Flask(__name__)


@app.route('/slave/sequence', methods=['PUT'])
def put_sequence():
    slave.set_sequence(request.get_json(force=True))


@app.route('/slave/execution', methods=['POST'])
def register_execution():
    slave.register_tasks(float(request.args.get('start_time')))
    # TODO spawn slave.start()


@app.route('/slave/execution', methods=['DELETE'])
def stop_execution():
    slave.stop()


@app.route('/slave/chrony/tracking', methods=['GET'])
def get_chrony_tracking():
    return jsonify(chronyc_tracking())


if __name__ == '__main__':
    # TODO: spawn a job which calls PUT {master_ip}:5000/master/slaves every 5s

    # https://stackoverflow.com/questions/29882642/how-to-run-a-flask-application
    app.run(host='0.0.0.0', debug=True)
