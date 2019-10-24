#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
from bottle import request, get, post, static_file, route, run, template
import ibm_db_dbi as dbi
from itoolkit import *
from itoolkit.db2.idb2call import *  # for local jobs

import sys
sys.path.append('/home/PYTHONDEM/myflask/')
version = tuple(map(int, dbi.__version__.split('.')))
if version < (2, 0, 5, 5):
    raise Exception("Need ibm_db_dbi 2.0.5.5 or higher to run, you have " + dbi.__version__)

@route('/',method='GET')
def sample():
    return static_file('mainscreen.html', root='.')

@route('/enquery', method='POST')
def query_ibm_db():
    sel_type = request.forms.get('select')
    values = request.forms.get('values')
    print(sel_type,values)
    if sel_type =='name':
        sql = "select * from PYTHONDEM1.USER_INFO WHERE USER_NAME ={}"
        statement = sql.format("'"+ values +"'")
    if sel_type == 'status':
        sql = "select * from PYTHONDEM1.USER_INFO WHERE STATUS ={}"
        statement = sql.format("'" + values + "'")
    if sel_type == 'library':
        sql = "select * from PYTHONDEM1.USER_INFO WHERE CURLIB ={}"
        statement = sql.format("'" + values + "'")
    if sel_type == 'jobd':
        sql = "select * from PYTHONDEM1.USER_INFO WHERE JOBD ={}"
        statement = sql.format("'" + values + "'")
    if sel_type == 'All':
        statement = "select * from PYTHONDEM1.USER_INFO"
    print(statement)
    conn = dbi.connect()
    cur = conn.cursor()
    cur.execute(statement)

    headers = [descr[0] for descr in cur.description]

    return template('tablescreen', headers=headers, rows=cur)

run(host='0.0.0.0', port=9110, debug=True, reloader=True)

