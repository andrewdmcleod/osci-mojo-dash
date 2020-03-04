import json
from flask import Flask, render_template
from collections import OrderedDict


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ugf uyfyitdy fougiuf iytfciygvc iygcycyi'

@app.route('/')
def index():
    # for x in data:
    with open('mojospecs_output.json') as json_file:
        DATA = json.load(json_file, object_pairs_hook=OrderedDict)
    for key, value in DATA.items():
        print(key, value)
    return render_template('index.html', data=DATA)

#@app.route('/history')
#def index_history():
#    # for x in data:
#    with open('results_os_upgrade.json') as json_file:
#        DATA = json.load(json_file)
#    for key, value in DATA.items():
#        print(key, value)
#    return render_template('index.html', data=DATA)

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5001)
