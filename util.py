import datetime
import os, time

def getDateTime(timestamp):
    os.environ['TZ'] = 'America/Los_Angeles'
    time.tzset()
    return datetime.datetime.fromtimestamp(int(timestamp))