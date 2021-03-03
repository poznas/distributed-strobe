#!flask/bin/python
import sys

from flask import Flask, request

from strobe_master import StrobeMaster

master = None

app = Flask(__name__)


@app.route('/master/slaves', methods=['PUT'])
def register_slave():
    master.register_slave(request.args.get('node_id'), request.remote_addr)


@app.route('/master/sequence/publish', methods=['POST'])
def register_execution():
    master.publish_offsets()


@app.route('/master/execution', methods=['POST'])
def register_execution():
    master.register_tasks(float(request.args.get('start_time')))
    print(f"TODO: spawn .start()")


@app.route('/master/execution', methods=['DELETE'])
def stop_execution():
    master.stop()


if __name__ == '__main__':
    master = StrobeMaster(sys.argv[1], sys.argv[2])

    app.run(host='0.0.0.0', debug=True)
