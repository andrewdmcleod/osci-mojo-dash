import json, glob
from flask import Flask, render_template
from collections import OrderedDict


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ugf uyfyitdy fougiuf iytfciygvc iygcycyi'

#test_date = "2020-08-27"
#file_name = "mojospecs_{}.json".format(test_date)
dated_files = glob.glob("mojospecs_2*.json")
dated_files.sort(reverse=True)

@app.route('/')
def index():
    # for x in data:
    with open('mojospecs_output.json') as json_file:
        DATA = json.load(json_file, object_pairs_hook=OrderedDict)
    for key, value in DATA.items():
        print(key, value)
    return render_template('index.html', links=dated_files, data=DATA)


@app.route('/<date>')
def index_history(date):
    # for x in data:
    for filename in dated_files:
        #date = filename.split("_")[1].split(".")[0]
        file_name = "mojospecs_{}.json".format(date)
    with open(file_name) as json_file:
        DATA = json.load(json_file, object_pairs_hook=OrderedDict)
    for key, value in DATA.items():
        print(key, value)
    return render_template('index.html', links=dated_files, data=DATA)


  
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
