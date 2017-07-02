import datetime
import time


def isoDateToZonedDatetime (isodate):
    
    gmtime_part = isodate[:19]
    zone_delta_H = isodate[19:22]
    zone_delta_M = isodate[23:]
    
    strptime_compatible_date = gmtime_part + zone_delta_H + zone_delta_M
    
    dt = datetime.datetime.strptime(strptime_compatible_date, '%Y-%m-%dT%H:%M:%S%z')
    
    return dt

def isoDateToLocalDatetime (isodate):
    
    gmtime_part = isodate[:19]
    zone_delta_H = isodate[19:22]
    zone_delta_M = isodate[23:]
    
    strptime_compatible_date = gmtime_part + zone_delta_H + zone_delta_M
    
    dt = datetime.datetime.strptime(gmtime_part, '%Y-%m-%dT%H:%M:%S')
    
    return dt
    
    


now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

start='2017-07-01T18:30:00+02:00'
end='2017-07-01T20:30:00+02:00'

dt_start = isodateToDatetime (start)
local_dt_start = isodateToLocalDatetime (start)
dt_end = isodateToDatetime (end)
local_dt_end = isodateToLocalDatetime (end)

zz = dt_end - dt_start

dt_now = datetime.datetime.now()

TT = dt_now - local_dt_start

later_than_start = local_dt_start < dt_now
earlier_than_end = dt_now < local_dt_end



time.strptime(start, '%Y-%m-%dT%H:%M:%S+%z')


datetime_start = datetime.datetime.utcfromtimestamp(start + 'Z')

x = 3


