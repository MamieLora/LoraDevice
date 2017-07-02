#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""Simple command-line sample for the Calendar API.
Command-line application that retrieves the list of the user's calendars."""

import sys
import time

import argparse
import logging

import logging

# create logger
logger = logging.getLogger('MamieLoraLogger')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


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
    
def isoDateToZonedDatetime (isodate):
    
    gmtime_part = isodate[:19]
    zone_delta_H = isodate[19:22]
    zone_delta_M = isodate[23:]
    
    strptime_compatible_date = gmtime_part + zone_delta_H + zone_delta_M
    
    dt = datetime.datetime.strptime(strptime_compatible_date, '%Y-%m-%dT%H:%M:%S%z')
    
    return dt

def isoDateToLocalDatetime (isodate):
    
    gmtime_part = isodate[:19]
    
    dt = datetime.datetime.strptime(gmtime_part, '%Y-%m-%dT%H:%M:%S')
    
    return dt
    
    

def updateMamieLoraDeviceStatus (device_status):
    
    global _device_status_to_remote_bin_value_table
    
    url = 'https://lpwa.liveobjects.orange-business.com/api/v0/vendors/lora/devices/0102030405060789/commands'
    # url = 'http://lpwa.liveobjects.orange-business.com/api/v0/vendors/lora/devices/0102030405060789/commands'
    
    headers = {}
    
    headers["Content-Type"] = "application/json;charset=UTF-8"
    headers["Accept"] = "application/json"
    headers["X-API-KEY"] = "6e1eefa3b6bc4fadb9158bbd2bbf587c"
    
    if not device_status in _device_status_to_remote_bin_value_table:
        logger.critical('Internal error. Status "%s" unknown' % device_status)
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
        
        req = urllib.request.Request(url=url, headers=headers, data=request_body, method='POST')

        response = urllib.request.urlopen(req, timeout=10)
        b_data = response.read()
        response_data = b_data.decode('utf-8')
        
        logger.debug (response_data)
        
    except urllib.error.HTTPError as e:
        logger.error (e)
        logger.error('The server couldn\'t fulfill the request.')
        logger.error('Error code: ', e.code)
  
    except urllib.error.URLError as e:
        logger.error('We failed to reach a server.')
        logger.error('Reason: ', e.reason)


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
        ch.setLevel(logging.DEBUG)
        # 'application' code
        logger.debug('Debug level activated')

        
    if args.proxy_host:
        set_http_proxy_configuration (args.proxy_host, args.proxy_port)

    logger.debug('setting to initial state = BLUE')    
    updateMamieLoraDeviceStatus ('BLUE')

    if False:
        logger.debug('setting to green')    
        updateMamieLoraDeviceStatus ('GREEN')
        time.sleep(1)
        logger.debug('setting to red')        
        updateMamieLoraDeviceStatus ('RED')
        time.sleep(1)
        logger.debug('setting to OFF')      
        updateMamieLoraDeviceStatus ('OFF')
 

    try:
        
        while True:

            dt_now = datetime.datetime.utcnow()
            now = dt_now.isoformat() + 'Z' # 'Z' indicates UTC time
            logger.debug('Getting current active event')
            eventsResult = service.events().list(
                calendarId='primary', timeMin=now, maxResults=1, singleEvents=True,
                orderBy='startTime').execute()
                
            events = eventsResult.get('items', [])

            if not events:
                logger.info('Currently no appointment.')
                updateMamieLoraDeviceStatus ('BLUE') 
            for event in events:
                iso_start = event['start'].get('dateTime', event['start'].get('date'))
                iso_end = event['end'].get('dateTime', event['end'].get('date'))
                
                local_time_start_dt = isoDateToLocalDatetime(iso_start)
                local_time_end_dt = isoDateToLocalDatetime(iso_end)
                description = event['description']
                logger.info('Next appointment start: %s' % iso_start)
                logger.info('Appointment description: %s' % description)
                
                # check if we are currently in an appointment
                later_than_start = local_time_start_dt < dt_now
                earlier_than_end = dt_now < local_time_end_dt
                
                if (later_than_start and earlier_than_end):
                    # the appointment is active
                
                    # check if it is a certified appointment
                    if 'keeex' in description:
                        logger.info ('KeeeX validated appointment')
                        updateMamieLoraDeviceStatus ('GREEN')
                    else:
                        logger.info ('Not a KeeeX validated appointment')
                        updateMamieLoraDeviceStatus ('RED')
                else:
                                      
                    logger.info ('Not a KeeeX validated appointment')
                    updateMamieLoraDeviceStatus ('BLUE')
                    
                
            time.sleep(20)
            
        
    except client.AccessTokenRefreshError:
        logger.critical('The credentials have been revoked or expired, please re-run'
              'the application to re-authorize.')

if __name__ == '__main__':
    main(sys.argv)