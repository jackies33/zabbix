

from flask import Flask, render_template, request, jsonify
import sys

sys.path.append('/opt/zabbix_custom/')

from start import start_export_devices

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    result = start_export_devices()
    return jsonify({'message': result})


if __name__ == '__main__':
    app.run(debug=True, host='10.50.174.34',port=5050)




