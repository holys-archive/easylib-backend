#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from pyquery import PyQuery as pq
import requests
import xml.etree.ElementTree as ET
import re


ISBN_SEARCH = 'http://opac.gdufs.edu.cn:8991/X?op=find&code=isb&request=%s&base=gwd01'
ISBN_PAGE = 'http://opac.gdufs.edu.cn:8991/F/?func=find-b&find_code=ISB&request=%s'

application = app = Flask('wsgi')


#def has_book(isbn):
#    """If has book return True, else False"""
#
#    url = ISBN_SEARCH % isbn
#    res = requests.get(url, stream=True)
#    print requests.get(url)
#    root = ET.parse(res.raw).getroot()
#    elem = root.find('no_records')
#    if elem is not None:
#        if int(elem.text) > 0:
#            return True
#        else:
#            return False
#    else:
#        return False

    

@app.route('/')
def index():
    return "hey buddy"

@app.route('/j/book/<isbn>')
def parse_table(isbn):
    """Parse search result html table and return pure data"""

    url = ISBN_PAGE % isbn
    page = requests.get(url)
    page.encoding = 'utf-8'
    d = pq(page.text)
    if d('#feedbackbar img'):
        return 'False'
    link = re.compile(ur'HREF=(.+?)>所有单册</a>', re.I).findall(page.text)
    if not link:
        return 'False'
    query = pq(link[0])
    tables = query('table')
    result = []
    for tr in tables[6]:
        try:
            text = pq(tr)('td.td1').text().split(' ')
            if len(text) == 6:
                result.append({
                    'loan_status': text[1].strip(),
                    'due_date': text[2].strip(),
                    'sub_library': text[3].strip(),
                    'location': text[4].strip()
                    })
            elif len(text) >= 7:
                result.append({
                    'loan_status': text[2],
                    'due_date': text[3],
                    'sub_library': text[4],
                    'location': text[5]
                    })
            elif len(text) == 4:
                result.append({
                    'loan_status': text[1],
                    'due_date': text[2],
                    'sub_library': text[3],
                    'location': ''
                    })
            else:
                return 'UnknownError'

        except AttributeError:
            pass
        except TypeError:
            pass
    return  jsonify({'books': result})


if __name__ == '__main__':
    app.run(debug=True)
