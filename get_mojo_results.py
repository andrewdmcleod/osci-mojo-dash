#!/usr/bin/python3

# Script fetches mojospec results from osci and dumps to 2 json files

import urllib.request, json , os, time, keyboard, sys, re, operator
from collections import OrderedDict
import time
import copy

os.environ['http_proxy'] = ''

numBuilds = 100
valid_configs = [
'trusty-mitaka',
'xenial-mitaka',
'xenial-newton',
'xenial-ocata',
'xenial-pike',
'xenial-queens',
'bionic-queens',
'bionic-rocky',
'bionic-stein',
'bionic-train',
'eoan-train'
]

all_urls = { 'os_upgrade': "http://osci:8080/view/MojoMatrix/job/test_mojo_openstack_upgrade_master_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fnext_openstack_upgrade,U_OS=",
            'charm_upgrade': "http://osci:8080/view/MojoMatrix/job/test_mojo_charm_upgrade_ha_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fstable_to_next_ha,U_OS=",
            'designate_ha': "http://osci:8080/view/MojoMatrix/job/test_mojo_designate_ha_master_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fnext_designate_ha,U_OS=",
            'vrrp_ha': "http://osci:8080/view/MojoMatrix/job/test_mojo_vrrp_ha_master_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fnext_ha_vrrp,U_OS=",
            'series_upgrade': "http://osci:8080/view/MojoMatrix/job/test_mojo_series_upgrade_master_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fnext_series_upgrade,U_OS="
           }

count = 1 
matrix = {}
matrix_full = {}
matrix_last = {}
addrow = False
configs = {}
configss = {}

for cur_url in all_urls.items():
    configss = {}
    matrix = {}
    print(cur_url[1])
    for current_config in valid_configs:
        count += 1
        lastline = ""
        if "trusty" in current_config:
            sortby = 0
        if "xenial" in current_config:
            sortby = 1
        if "bionic" in current_config:
            sortby = 2
        try:
            with urllib.request.urlopen("{}{}/lastBuild/api/json/".format(cur_url[1],current_config)) as jsonurl:
                jsdata = json.loads(jsonurl.read().decode())
                timestamp=jsdata['timestamp']
                displayName=jsdata['fullDisplayName']
                url=cur_url[1] + current_config + "/lastBuild/"
                result=jsdata['result']
                specName=cur_url[0]
                config=jsdata['url'].split('/')[7].split('=')[2]
                datetime = time.strftime('%Y-%m-%d', time.gmtime(jsdata['timestamp'] / 1000))
        except:
            config=current_config
            timestamp="0"
            datetime="0"
            result="EMPTY"
            url="null"
            specName=cur_url[0]
        if config in valid_configs:
            configs = {config: {
                        'timestamp': datetime,
                        'config': config,
                        'result': result,
                        'sortby': sortby,
                        'url': url
                       }}
            configss.update(sorted(configs.items()))
            matrix = {specName: {
                      'url': url,
                      'specName': specName,
                      'config': configss,
                      }}
            matrix_full.update(matrix)
            filename = "mojospecs_output.json".format(specName)


def sortit(d):

    def extract(x):
        # assumes only one key in the x dictionary
        print(x)
        k = list(x.keys())[0]
        v = x[k]
        return (k, v)

    def sortby(x):
        (k, v) = extract(x)
        return (v['sortby'], k)

    li = [{k: v} for k, v in d['config'].items()]
    sl = sorted(li, key=sortby)
    dd = copy.deepcopy(d)
    dd['config'] = OrderedDict([extract(x) for x in sl])
    return dd


def sortall(d):
    return {k: sortit(v) for k, v in d.items()}


matrix_sorted = sortall(matrix_full)

with open(filename, 'w') as outfile:
    json.dump(matrix_sorted, outfile)

