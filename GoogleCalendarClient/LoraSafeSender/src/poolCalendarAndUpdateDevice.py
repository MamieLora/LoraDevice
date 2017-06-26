#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""Simple command-line sample for the Calendar API.
Command-line application that retrieves the list of the user's calendars."""

import sys
import time

import argparse

from oauth2client import client
from googleapiclient import sample_tools

import datetime

_calendar_id = 'mamie.lora06@gmail.com'
_found_calendar = None

_mamie_lora_private_key = '%x%x%x%x' % (72, 73, 27, 37)
_device_status_to_remote_bin_value_table = {
    'RED': '01',
    'BLUE': '02',
    'GREEN': '03',
    'OFF': '00'
}

'''
########################################"
MamieLora interface functions
'''

import http.client
import urllib.request
import json

_debug = False
def activate_http_debug ():
    global _debug
    
    _debug = True
    
    http.client.HTTPConnection.debuglevel = 1
    http.client.HTTPSConnection.debuglevel = 1
    
_urllib_proxy_specification = {}    

def set_http_proxy_configuration (proxy_host, proxy_port = None):
    global _urllib_proxy_specification
    
    if proxy_port:
        proxy_url = 'http://%s:%d/' % (proxy_host, proxy_port)
    else:
        proxy_url = 'http://%s:8080/' % proxy_host
        
    _urllib_proxy_specification = {'http': proxy_url, 'https': proxy_url }

def updateMamieLoraDeviceStatus (device_status):
    
    global _device_status_to_remote_bin_value_table
    
    url = 'https://lpwa.liveobjects.orange-business.com/api/v0/vendors/lora/devices/0102030405060789/commands'
    headers = {}
    
    headers["Content-Type"] = "application/json;charset=UTF-8"
    headers["Accept"] = "application/json"
    headers["X-API-KEY"] = "6e1eefa3b6bc4fadb9158bbd2bbf587c"
    
    if not device_status in _device_status_to_remote_bin_value_table:
        print('Internal error. Status "%s" unknown' % device_status)
        return
    
    remote_bin_value_for_status = _device_status_to_remote_bin_value_table[device_status]
    
    json_body_arg = {
        "data": "%s%s" % (_mamie_lora_private_key, remote_bin_value_for_status),
        "port": "1",
        "confirmed": "false"        
    }
    
    
    json_str = json.dumps (json_body_arg)
    
    request_body = json_str.encode(encoding='utf_8')
    
    try:
        
        if _debug:
            http_debug_level_flag = 1
        else:
            http_debug_level_flag = 0
        
        http_handler = urllib.request.HTTPHandler(debuglevel=http_debug_level_flag)
        
        proxy_handler = urllib.request.ProxyHandler (_urllib_proxy_specification)
        
        opener = urllib.request.build_opener(http_handler, proxy_handler)

        # install it
        urllib.request.install_opener(opener)
        
        req = urllib.request.Request(url=url, headers=headers, data=request_body, method='GET')

        response = urllib.request.urlopen(req, timeout=10)
        b_data = response.read()
        response_data = b_data.decode('utf-8')
        
        print (response_data)
        
    except urllib.error.HTTPError as e:
        print (e)
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
  
    except urllib.error.URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)


def main(argv):

    
    parser = argparse.ArgumentParser(add_help=False)
    
    parser.add_argument("--proxy_host", type=str, help='proxy hostname if a HTTP proxy has to be used')
    parser.add_argument("--proxy_port", type=int, help='proxy port number associated with --proxy_host is specified')    
    parser.add_argument("--debug", action='store_true')
    
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar.readonly',
        parents=[parser]) 
    
    args = parser.parse_args()
    
    if args.debug:
        activate_http_debug()
        
    if args.proxy_host:
        set_http_proxy_configuration (args.proxy_host, args.proxy_port)
    
    updateMamieLoraDeviceStatus ('BLUE')
    sys.exit(1)
    time.sleep(4000)
    updateMamieLoraDeviceStatus ('RED')
    sys.exit(1)

    try:
        page_token = None
        
        
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        eventsResult = service.events().list(
            calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
            
        events = eventsResult.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

        
        while True:
            calendar_list = service.calendarList().list(
                pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                
                print(calendar_list_entry['summary'])
                
                calendarId = calendar_list_entry['id']
                if calendarId == _calendar_id:
                    _found_calendar = calendar_list_entry
                    break
                    
                
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        
        _found_calendar
        
    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run'
              'the application to re-authorize.')

if __name__ == '__main__':
    main(sys.argv)