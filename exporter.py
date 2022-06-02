# from ast import Continue
# from ctypes import util
# from urllib import request
# from flask import Flask, request
from flask import Flask
import requests
import re
from re import search
from datetime import datetime
import getopt, sys
import time
from bs4 import BeautifulSoup
import locale
import os.path

def help():
    print("\nHelp\n")
    print("Execute:")
    print("    exporter.py [--username=<username>] \ ")
    print("                [--password=<password>] \ ")
    print("                [--port=<port>] \ ")
    print("                [--pages=<number of pages>]")
    print("                [--help]")
    print("    exporter.py --username=your.name@somedomain.org \ ")
    print("                --password=yoursecretpassword \ ")
    print("                --pages=30 \ ") 
    print("                --port=5000\n")
    print("Endpoints:")
    print("    # curl http://127.0.0.1:2000/metrics")
    print("    # curl http://127.0.0.1:2000/status\n")
    print("notes:")
    print("    Default number of pages is 10")
    print("    Default port: 5000\n")

def getCss():
    _css = '''    <style>
        div.navbar {
            position: absolute;
            top: 10px;
            right: 10px;
            left: 10px;
            background-color: #343a40;
            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
            font-size: 1.5rem;
            font-weight: 400;
            line-height: 1.5;
            color: #212529;
            text-align: left;
            padding: 10px;    
        }
        .white {
            color: #ffff;
            text-decoration: none; 
        }
        .white:hover {
            color: #c2c2d6;
        }
        .gray {
            color: #c2c2d6;
            text-decoration: none; 
        }
        .gray:hover {
            color: #ffff;
        }
        lu {
            padding: 10px;
        }
        div.bottom {
            position: absolute;
            bottom: 10px;
            right: 10px;
        }
        div.content {
            position: relative;
            top: 100px;
            right: 10px;
            left: 10px;
            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
            font-size: 1rem;
            font-weight: 400;
            line-height: 1.5;
            color: #212529;
            text-align: left;
            padding: 10px;    
        }
        </style>'''
    return _css

def getBottom():
    _bottom = '''    <div class="bottom">
            <a href="https://github.com/tedsluis/mysportsplanner-exporter">https://github.com/tedsluis/mysportsplanner-exporter</a>
        </div>'''
    return _bottom

def getHome():
    _home = '''<!DOCTYPE html>
    <html>
    <head>
    ''' + getCss() + '''
    </head>
    <body>
        <div class="navbar">
            <lu><a class="white" href="/">mysportsplanner-exporter</a></lu>
            <lu><a class="gray" href="/status">status</a></lu>
            <lu><a class="gray" href="/metrics">metrics</a></lu>
            <lu><a class="gray" href="https://github.com/tedsluis/mysportsplanner-exporter">help</a></lu>
        </div>
        <div class="content">
            ..........
        </div>
    ''' + getBottom() + '''
    </body>
    </html>
    '''
    return _home

def getStatus(_scrape_counter,_number_of_requests,_status_code,_response_time,_response_size,_scrape_time,_scrape_size,_utc_time_start_scrape):
    _status = '''<!DOCTYPE html>
    <html>
    <head>
    ''' + getCss() + '''
    </head>
    <body>
        <div class="navbar">
            <lu><a class="gray" href="/">mysportsplanner-exporter</a></lu>
            <lu><a class="white" href="/status">status</a></lu>
            <lu><a class="gray" href="/metrics">metrics</a></lu>
            <lu><a class="gray" href="https://github.com/tedsluis/mysportsplanner-exporter">help</a></lu>
        </div>
        <div class="content"; width: 100%;>
            <h1>
                <a href="/metrics">scrape status</a>
            </h1>
            <table border="1" bordercolor=gray cellpadding="3" cellspacing="0" style="width: 100%" >
                <thead>
                    <tr align="left">
                        <th>Last scrape</th>
                        <th>Scrape count</th>
                        <th>Scrape time</th>
                        <th>Scrape size</th>
                    </tr>
                </thead>
                <tbody>
                    <tr bgcolor="#dee2e6">
                        <td>''' + str((datetime.now().timestamp() - _utc_time_start_scrape)) + ''' sec ago</td>
                        <td>''' + str(_scrape_counter) + '''</td>
                        <td>''' + str(_scrape_time) + ''' seconds</td>
                        <td>''' + str(_scrape_size) + ''' bytes</td>
                    </tr>
                </tbody>
            </table>

            <h1>
                <a href="/metrics">target status</a>
            </h1>
            <table border="1" bordercolor=gray cellpadding="3" cellspacing="0" style="width: 100%" >
                <thead>
                    <tr align="left">
                        <th>Number of requests</th>
                        <th>HTTP status code</th>
                        <th>Response time</th>
                        <th>Response size</th>
                    </tr>
                </thead>
                <tbody>
                    <tr bgcolor="#dee2e6">
                        <td>''' + str(_number_of_requests) + '''</td>
                        <td>''' + str(_status_code) + '''</td>
                        <td>''' + str(_response_time) + ''' sec</td>
                        <td>''' + str(_response_size) + ''' bytes</td>
                    </tr>
                </tbody>
            </table>


            <h1>
                <a href="/metrics">event status</a>
            </h1>
            <table border="1" bordercolor=gray cellpadding="3" cellspacing="0" style="width: 100%" >
                <thead>
                    <tr align="left">
                        <th>Number of pages</th>
                    </tr>
                </thead>
                <tbody>
                    <tr bgcolor="#dee2e6">
                        <td>''' + str(_pages) + '''</td>
                    </tr>
                </tbody>
            </table>

        </div>
    ''' + getBottom() + '''
    <body>
    </html>
    '''
    return _status

def parameters(argv):
    _username = "admin"
    _password = "admin"
    _pages = 10
    _port = 5000
    try:
        opts, args = getopt.getopt(argv,"h",["username=","password=","pages=","port="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--help':
            help()
            sys.exit()
        elif opt in ("--username"):
            _username = arg
        elif opt in ("--password"):
            _password = arg
        elif opt in ("--pages"):
            _pages = arg
        elif opt in ("--port"):
            _port = arg
    print ('username is:', _username)
    print ('password is:', _password)
    print ('pages is:', _pages)
    print ('port is:', _port)
    return (_username,_password,_pages,_port)

def responseMetrics(_response,_url,_status,_metrics):
    _response_time = _response.elapsed.microseconds / 1000000
    print('_response_time1: %s' % _response_time)
    _metrics.append('# HELP mysportplanner_scrape_response_time_seconds Number of seconds elapsed')
    _metrics.append('# TYPE mysportplanner_scrape_response_time_seconds gauge')
    _metrics.append('mysportplanner_scrape_response_time_seconds{url="' + _url + '",status="' + _status + '"} ' + str(_response_time))
    _response_size = len(_response.text)
    print('_response_size: %s' % _response_size)
    _metrics.append('# HELP mysportplanner_scrape_response_size_bytes Number of bytes')
    _metrics.append('# TYPE mysportplanner_scrape_response_size_bytes gauge')
    _metrics.append('mysportplanner_scrape_response_size_bytes{url="' + _url + '",status="' + _status_code + '"} ' + str(_response_size))
    return _response_time,_response_size,_metrics

def createSession(_metrics):
    print('----- create session--------------')
    with requests.Session() as _session:
        _session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        _status = ""
        _timeout = 1
        _url = 'https://mysportsplanner.com/default.asp?ln=nl'
        print(_url)
        _retry1 = 0
        while (not search('^2\d*', _status)) and (_retry1 < 3):
            _retry1 += 1
            _timeout = (1 + _retry1 * 2)
            # _response = _session.get(_url)
            try:
                _response = _session.get(_url, timeout=_timeout)
            except:
                pass
            else:
                _status = str(_response.status_code)
            print('STATUS: %s, number of requests: %s' % (_status,_retry1))
            time.sleep(1)

        _response_time1,_response_size1,_metrics = responseMetrics(_response,_url,_status,_metrics)

        if not search('^2\d*', _status):
            return _session,_status,_response_time1,_response_size1,_retry1,_metrics
            
        _soup = BeautifulSoup(_response.text,'html.parser')   
        _payload = {i['name']:i.get('value','') for i in _soup.select('input[name]')}         
        _payload['username'] = _username
        _payload['password'] = _password
        print('payload: %s\n' % _payload)

        _status = ""
        _url = 'https://mysportsplanner.com/default.asp?ln=nl&login=true'
        print(_url)
        _retry2 = 0
        while (not search('^2\d*', _status)) and (_retry2 < 3):
            _retry2 += 1
            _timeout = (1 + _retry2 * 2)
            try:
                _session.post(_url,data=_payload, timeout=_timeout)
            except:
                pass
            else:
                _status = str(_response.status_code)
            print('STATUS: %s, number of requests: %s' % (_status,_retry2))
            time.sleep(1)

        _response_time2,_response_size2,_metrics = responseMetrics(_response,_url,_status,_metrics)
        
        return _session,_status,(_response_time1 + _response_time2),(_response_size1 + _response_size2),(_retry1 + _retry2),_metrics

def getPage(_session,_url,_metrics):
    print('----- get page -------------------')
    print('url: %s\n' % _url)
    _status = ""
    _timeout = 1
    _retry = 0
    while (not search('^2\d*', _status)) and (_retry < 3):
        _retry += 1
        _timeout = (1 + _retry * 2)
        try:
            _response = _session.get(_url, timeout=_timeout)
        except:
            pass
        else:
            _status = str(_response.status_code)
        print('STATUS: %s' % _status)
        time.sleep(1)

    _response_time,_response_size,_metrics = responseMetrics(_response,_url,_status,_metrics)
    # print('response text: %s\n' % _response.text)
    _soup = BeautifulSoup(_response.content, 'html.parser')
    return _soup,_status,_response_time,_response_size,_retry,_metrics

def getStartAndEnd(_soup):
    print('---- get start and end of period -------')
    print('_soup: %s' % _soup)
    _schedule_paging = _soup.find(id="schedule_paging")
    print('_schedule_paging: %s' %_schedule_paging)
    _span = _schedule_paging.find_all("span")
    _span0 = _span[0]
    _start = int(str(_span0.find("a")).split("page=")[1].split('&amp')[0]) + 6
    _span2 = _span[2]
    _end = int(str(_span2.find("a")).split("page=")[1].split('&amp')[0]) -1
    print("schedule_paging start: %s, end: %s, next: %s\n" % (_start,_end,_end + 1))
    return _start,_end,_end +1

def getMembers(_soup):
    print('---- get members --------------------')
    _member_full_names = {}
    _member_emails = {}
    _member_type = {}
    _member_phone = {}
    _member_ids = {}
    _class_teammembers = _soup.find_all(class_="teammember")
    for _class_teammember in _class_teammembers:
        _class_fullname = _class_teammember.find(class_="full_name")
        _full_name = str(_class_fullname.find("a")).split('">')[1].split('<')[0].replace('   ',' ').replace('  ',' ')
        _class_email = _class_teammember.find(class_="email")
        _email = str(_class_email.find("a")).split('">')[1].split('<')[0]
        _class_type = _class_teammember.find(class_="type")
        _type = str(_class_type).split('">')[1].split('<')[0]
        _class_phone = _class_teammember.find(class_="phone")
        _phone = ""
        if not search('phone"><', str(_class_phone)):
            _phone = str(_class_phone).split('">')[1].split('<')[0]
        _id = str(_class_fullname.find("a")).split("id=")[1].split('"')[0]
        print('member_id=%8s                full name=%35s        email=%40s     type=%s     phone=%s' % (_id,_full_name,_email,_type,_phone))
        _member_full_names[_id] = _full_name
        _member_emails[_id] = _email
        _member_type[_id] = _type
        _member_phone[_id] = _phone
        _member_ids[_full_name] = _id
    return _member_full_names,_member_emails,_member_type,_member_phone,_member_ids

def getDayDutch(_date):
    _utc_date = datetime.strptime(_date,"%d-%m-%Y").timestamp()
    locale.setlocale(category=locale.LC_ALL, locale='nl_NL.utf8')
    _dag = datetime.fromtimestamp(_utc_date).strftime("%A")
    return _dag

def getHeader(_soup,_id,_event_date,_event_dag,_event_time,_event_activity):
    print('---- get header --------------------')
    _schedule = _soup.find(id="schedule")
    _event_id = _id
    for _class_date in _schedule.find_all(class_="date"):
        _date = str(_class_date.find("a")).split('</span>')[1].split('</a')[0]
        _dag = getDayDutch(_date)
        _event_date[_event_id] = _date
        _event_dag[_event_id] = _dag
        _event_id += 1
        #print('date=%s     day=%s    id=%s' % (_date,_dag))
    _event_id = _id
    for _class_time in _schedule.find_all(class_="time"):
        _time = str(_class_time.find("span")).split('<span>')[1].split('</span')[0]
        _event_time[_event_id] = _time
        #print('time=%s' % (_time))
        _event_id += 1
    _event_id = _id
    for _class_activity in _schedule.find_all(class_="activity"):
        _activity = str(_class_activity).split('"activity">')[1].split('</p')[0].replace('.','')
        #print('activity=%s' % (_activity))
        _event_activity[_event_id] = re.sub('Tra.*', 'Training', _activity)
        _event_id += 1
    return _event_date,_event_dag,_event_time,_event_activity

def getFullName(_name,_member_full_names):
    _name = str(re.sub('\.*$', '', _name)).lower()
    for _member_id,_full_name in _member_full_names.items():
        if re.search(_name, _full_name.lower()):
            return _full_name
    return _name

def getParticipants(_soup,_perticipants,_member_full_names):
    print('---- get participation --------------------')
    _schedule = _soup.find(id="schedule")
    for _class_name in _schedule.find_all(class_="name"):
        _name = str(_class_name).split('>')[1].split('<')[0]
        _member_full_name = getFullName(_name,_member_full_names)
        print('name: %35s   fullname %35s' % (_name,_member_full_name))
        _perticipants.append(_member_full_name)
    return _perticipants

def getTeamname(_soup,_team_name):
    print('---- get participation --------------------')
    _schedule = _soup.find(id="schedule")
    for _class_type in _schedule.find_all(class_="type"):
        _team = str(_class_type).split('>')[1].split('<')[0]
        print('team: %35s ' % (_team))
        _team_name.append(_team)
    return _team_name

def getParticipation(_soup,_start_id,_end_id,_perticipants,_team_name,_member_ids,_member_team,_participation,_memo):
    print('---- get participation --------------------')
    _schedule = _soup.find(id="schedule")
    _event_id = _start_id
    _row = 0
    for _class_av_box in _schedule.find_all(class_="av_box"):
        _member_full_name = _perticipants[_row]
        _member_id = _member_ids[_member_full_name]
        _member_team[_member_id] = _team_name[_row]
        _index = str(_event_id) + '-' + _member_id
        if 'av-0' in str(_class_av_box):
            _participation[_index] = "niet gepland"
        elif 'av-1' in str(_class_av_box):
            _participation[_index] = "aanwezig"
        elif 'av-2' in str(_class_av_box):
            _participation[_index] = "afwezig"
        else:
            print('not found')
        _class_memo=str(_class_av_box.find(class_="memo"))
        # print("CLASSMEMO: %s" % str(_class_memo))
        if search('None', _class_memo):
            _memo[_index] = ""
        elif search('rel=".+"', _class_memo):
            _memo[_index] = str(_class_memo).split('rel="')[1].split('"')[0]
        else:    
            _memo[_index] = ""
        print(_event_id,_participation[_index],_memo[_index],end=" ")
        if _event_id == _end_id:
            _event_id = _start_id
            _row += 1
            print(_member_id, _member_full_name,_member_team[_member_id])
        else:
            _event_id += 1
    return _member_team,_participation,_memo

def persistParticipantion(_event_id,_member_id,_presence):
    print('--- persist participation -------------')
    _filename = 'event_' + str(_event_id) + '-member_' + str(_member_id) + '.txt'
    if _presence == "niet gepland" and os.path.isfile(_filename):
        print('remove %s' % _filename)
        os.remove(_filename)
        return 0
    elif _presence == "niet gepland" and not os.path.isfile(_filename):
        return 0
    elif os.path.isfile(_filename) and (_presence == "aanwezig" or _presence == "afwezig"):
        f = open(_filename, "r")
        _epoch = float(f.readline())
        _now = datetime.now().timestamp()
        f.close()
        if _presence == "aanwezig" and _epoch > 0:
            _duration = _now - _epoch
        elif _presence == "afwezig" and _epoch < 0:
            _duration = _now + _epoch
        else:
            _now = datetime.now().timestamp()
            if _presence == "aanwezig" and _epoch < 0:
                f = open(_filename, "w")
                f.write(str(_now))
                f.close()
                print('write: %s, %s' % (_filename,_now))
            elif _presence == "afwezig" and _epoch > 0:
                f = open(_filename, "w")
                f.write(str(-_now))
                f.close()
                print('write: %s, %s' % (_filename,-_now))
            else:
                return 0
            return 0
        print('read content: %s, %s' % (_filename,_duration))
        return _duration
    elif not os.path.isfile(_filename) and (_presence == "aanwezig" or _presence == "afwezig"):
        _now = datetime.now().timestamp()
        f = open(_filename, "w")
        if _presence == "aanwezig":
            f.write(str(_now))
            print('write: %s, %s' % (_filename,_now))
        else:
            f.write(str(-_now))
            print('write: %s, %s' % (_filename,-_now))
        f.close()
        return 0
    else:
        print('do nothing')
    return

def createMetrics(_metrics,_participation,_memo,_member_full_names,_member_emails,_member_type,_member_phone,_member_team,_event_date,_event_dag,_event_time,_event_activity,_status_code,_scrape_counter,_response_time,_response_size,_scrape_time,_scrape_size,_number_of_requests):
    print('--- create metrics -------------')

    _metrics.append('# HELP mysportplanner_schedule number of seconds since planned')
    _metrics.append('# TYPE mysportplanner_schedule counter')
    for _index in _participation.keys():
        _member_id = _index.split('-')[1]
        _event_id = int(_index.split('-')[0])
        _presence = _participation[_index]
        print('_member_id: %s, _event_id: %s, _presence: %s' % (_member_id,_event_id,_presence))
        _duration = persistParticipantion(_event_id,_member_id,_presence)
        _utc_time_now = datetime.now().timestamp()
        _datum = datetime.fromtimestamp(_utc_time_now - _duration).strftime("%Y-%m-%d %H:%M:%S %a")
        _metrics.append(\
            'mysportplanner_schedule{member_id="' + str(_member_id) + \
            '",member_full_name="' + _member_full_names[_member_id] + \
            '",member_email="' + _member_emails[_member_id] + \
            '",member_type="' + _member_type[_member_id] + \
            '",member_phone="' + _member_phone[_member_id] + \
            '",member_team="' + _member_team[_member_id] + \
            '",event_id="' + str(_event_id) + \
            '",presence="' + _presence + \
            '",event_date="' + _event_date[_event_id] + \
            '",event_day="' + _event_dag[_event_id] + \
            '",event_time="' + _event_time[_event_id] + \
            '",last_changed="' + str(_datum) + \
            '",memo="' + _memo[_index] + \
            '",event_activity="' + _event_activity[_event_id] + '"} ' + str(_duration))

    _metrics.append('# HELP mysportplanner_scrape_counter Number of scrapes since exporter started')
    _metrics.append('# TYPE mysportplanner_scrape_counter counter')
    _metrics.append('mysportplanner_scrape_counter{status_code="' + _status_code + '"} ' + str(_scrape_counter))

    _metrics.append('# HELP mysportplanner_number_of_requests number of requests')
    _metrics.append('# TYPE mysportplanner_number_of_requests gauge')
    _metrics.append('mysportplanner_number_of_requests ' + str(_number_of_requests)) 

    _metrics.append('# HELP mysportplanner_response_time number of seconds')
    _metrics.append('# TYPE mysportplanner_response_time gauge')
    _metrics.append('mysportplanner_response_time ' + str(_response_time))  

    _metrics.append('# HELP mysportplanner_scrape_time number of seconds')
    _metrics.append('# TYPE mysportplanner_scrape_time gauge')
    _metrics.append('mysportplanner_scrape_time ' + str(_scrape_time))  

    _metrics.append('# HELP mysportplanner_response_size number of bytes')
    _metrics.append('# TYPE mysportplanner_response_size gauge')
    _metrics.append('mysportplanner_response_size ' + str(_response_size))  

    _metrics.append('# HELP mysportplanner_scrape_size number of lines')
    _metrics.append('# TYPE mysportplanner_scrape_size gauge')
    _metrics.append('mysportplanner_scrape_size ' + str(len(_metrics)))

    return _metrics

_username,_password,_pages,_port = parameters(sys.argv[1:])
print("_username: %s, password: %s, pages: %s, port: %s\n" % (_username,_password,_pages,_port))

_scrape_counter = 0
_number_of_requests = 0
_status_code = ""
_response_time = ""
_response_size = ""
_scrape_time = ""
_scrape_size = ""
_utc_time_start_scrape = datetime.now().timestamp()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    _home = getHome()
    return _home

@app.route('/metrics', methods=['GET'])
def metrics():

    global _scrape_counter
    global _number_of_requests
    global _status_code
    global _response_time
    global _response_size
    global _scrape_time
    global _scrape_size
    global _utc_time_start_scrape

    _metrics=[]
    _scrape_counter = _scrape_counter + 1
    _utc_time_start_scrape = datetime.now().timestamp()


    _event_date = {}
    _event_dag = {}
    _event_time = {}
    _event_activity = {}
    _member_full_names = {}
    _member_emails = {}
    _member_type = {}
    _member_phone = {}
    _member_ids = {}
    _member_team = {}
    _participation = {}
    _memo = {}

    # create session
    (_session,_status_code,_tmp_response_time,_tmp_response_size,_number_of_requests,_metrics) = createSession(_metrics)
    _cumulative_response_time = _tmp_response_time
    _cumulative_response_size = _tmp_response_size

    # get team members
    if _status_code == "200":
        (_soup_teammembers,_status_code,_tmp_response_time,_tmp_response_size,_numberofrequest,_metrics) = getPage(_session,'https://mysportsplanner.com/?action=teammembers',_metrics)
        _cumulative_response_time += _tmp_response_time
        _cumulative_response_size += _tmp_response_size
        _number_of_requests += _numberofrequest
        _member_full_names,_member_emails,_member_type,_member_phone,_member_ids = getMembers(_soup_teammembers)

        _url = 'https://mysportsplanner.com/default.asp?action=schedule'
        _current_page = _url
        _pagenumber = 0

    while _pagenumber < int(_pages) and _status_code == "200":

        print('page=%s,   currentpage=%s' % (_pagenumber,_current_page))
        _pagenumber += 1

        # get schedule
        (_soup_schedule,_status_code,_tmp_response_time,_tmp_response_size,_numberofrequest,_metrics) = getPage(_session,_current_page,_metrics)
        _cumulative_response_time += _tmp_response_time
        _cumulative_response_size += _tmp_response_size
        _number_of_requests += _numberofrequest

        # get start, end and next 
        (_start_period,_end_period,_start_next_period) = getStartAndEnd(_soup_schedule)
        print('start: %s, end: %s, next: %s' % (_start_period,_end_period,_start_next_period))

        # prep next schedule url
        _current_page = _url + '&page=' + str(_start_next_period) + '&order=1'

        # get header
        (_event_date,_event_dag,_event_time,_event_activity) = getHeader(_soup_schedule,_start_period,_event_date,_event_dag,_event_time,_event_activity)
        print(_event_dag)
        print(_event_date)
        print(_event_time)
        print(_event_activity)

        # get perticipants
        _perticipants = getParticipants(_soup_schedule,[],_member_full_names)

        # get teamname
        _team_name = getTeamname(_soup_schedule,[])

        # get perticipation
        (_member_team,_participation,_memo) = getParticipation(_soup_schedule,_start_period,_end_period,_perticipants,_team_name,_member_ids,_member_team,_participation,_memo)

    _utc_time_end_scrape = datetime.now().timestamp()
    _scrape_time = _utc_time_end_scrape - _utc_time_start_scrape
    _response_time = _cumulative_response_time
    _response_size = _cumulative_response_size

    (_metrics) = createMetrics(_metrics,_participation,_memo,_member_full_names,_member_emails,_member_type,_member_phone,_member_team,_event_date,_event_dag,_event_time,_event_activity,_status_code,_scrape_counter,_response_time,_response_size,_scrape_time,_scrape_size,_number_of_requests)
    _scrape_size = str(len(_metrics))
    
    return "\n".join(_metrics) + '\n'

@app.route('/status', methods=['GET'])
def status():
    _status = getStatus(_scrape_counter,_number_of_requests,_status_code,_response_time,_response_size,_scrape_time,_scrape_size,_utc_time_start_scrape)
    print(_status)
    return _status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=_port)