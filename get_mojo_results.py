#!/usr/bin/python3

# Script fetches mojospec results from osci and dumps to 2 json files

import urllib.request, json , os, time, keyboard, sys, re, operator
from collections import OrderedDict
from shutil import copyfile
import time
import copy

os.environ['http_proxy'] = ''

class E(Exception):
    pass

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
'focal-ussuri'
]

valid_func_configs = [
'trusty-mitaka',
'xenial-mitaka',
'bionic-queens',
'focal-ussuri'
]

all_urls = { 'os_upgrade': "http://osci:8080/view/MojoMatrix/job/test_mojo_openstack_upgrade_master_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fnext_openstack_upgrade,U_OS=",
            'charm_upgrade': "http://osci:8080/view/MojoMatrix/job/test_mojo_charm_upgrade_ha_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fstable_to_next_ha,U_OS=",
            'designate_ha': "http://osci:8080/view/MojoMatrix/job/test_mojo_designate_ha_master_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fnext_designate_ha,U_OS=",
            'vrrp_ha': "http://osci:8080/view/MojoMatrix/job/test_mojo_vrrp_ha_master_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fnext_ha_vrrp,U_OS=",
            'series_upgrade': "http://osci:8080/view/MojoMatrix/job/test_mojo_series_upgrade_master_matrix/MOJO_SPEC=specs%2Ffull_stack%2Fnext_series_upgrade,U_OS=",
            'ubuntu_lite': "http://osci:8080/view/FuncMatrix/job/test_func_series_upgrade_ubuntu_lite_matrix/TEST_PATH=development%2Fubuntu-lite-series-upgrade-",
            'cot_vrrp': "http://10.245.162.58:8080/job/test_func_vrrp_matrix/TEST_TOX_TARGET=vrrp-",
            'cot_sink': "http://10.245.162.58:8080/job/test_func_kitchen_sink_matrix/TEST_TOX_TARGET=kitchen-sink-",
            'cot_charm_upgrade': "http://10.245.162.58:8080/job/test_func_charm_upgrade_matrix/TEST_TOX_TARGET=charm-upgrade-"
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
    for current_config in valid_configs:
        count += 1
        lastline = ""
        if "trusty" in current_config:
            sortby = 0
        if "xenial" in current_config:
            sortby = 1
        if "bionic" in current_config:
            sortby = 2
        if "focal" in current_config:
            sortby = 3
        if "test_func_" in cur_url[1]:
            func = True
            func_config = current_config.split("-")[0]
            if "cot_" in cur_url[0]:
                func_config = current_config
        else:
            func = False
        try:
            if func:
                if current_config not in valid_func_configs:
                    print("{} not in valid_func_configs".format(current_config))
                    raise
                get_url = "{}{}/lastBuild/api/json/".format(cur_url[1],func_config)
                split_chr = '-'
                split_num = 4 
            else:
                get_url = "{}{}/lastBuild/api/json/".format(cur_url[1],current_config)
                split_chr = '='
                split_num = 2 
            with urllib.request.urlopen(get_url) as jsonurl:
                jsdata = json.loads(jsonurl.read().decode())
                timestamp=jsdata['timestamp']
                displayName=jsdata['fullDisplayName']
                if func:
                    url=cur_url[1] + func_config + "/lastBuild/"
                else:
                    url=cur_url[1] + current_config + "/lastBuild/"
                result=jsdata['result']
                building=jsdata['building']
                if building:
                    building="BUILDtrue"
                else:
                    building="BUILDfalse"
                specName=cur_url[0]
                print(jsdata['url'])
                try:
                    config=jsdata['url'].split('/')[7].split(split_chr)[split_num]
                except:
                    pass
                if func:
                    config = current_config
                datetime = time.strftime('%Y-%m-%d', time.gmtime(jsdata['timestamp'] / 1000))
        except urllib.error.HTTPError:
            config=current_config
            timestamp="0"
            datetime="0"
            result="EMPTY"
            building="BUILDfalse"
            url="null"
            specName=cur_url[0]
        except:
            config=current_config
            timestamp="0"
            datetime="0"
            result="EMPTY"
            building="BUILDfalse"
            url="null"
            specName=cur_url[0]
 
        if "vrrp" in url and "trusty-mitaka" in url:
            result="EMPTY"
        if config in valid_configs:
            configs = {config: {
                        'timestamp': datetime,
                        'config': config,
                        'result': result,
                        'building': building,
                        'sortby': sortby,
                        'url': url
                       }}
            configss.update(sorted(configs.items()))
            matrix = {specName: {
                      'url': url,
                      'specName': specName,
                      'config': configss,
                      }}
            print("Updating matrix: {}".format(matrix))
            matrix_full.update(matrix)
            filename = "mojospecs_output.json".format(specName)
        else:
            print("{} not found ".format(config))


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

dst_filename = "mojospecs_{}.json".format(time.strftime('%Y-%m-%d'))
copyfile(filename, dst_filename) 

with open(filename, 'w') as outfile:
    json.dump(matrix_sorted, outfile)


