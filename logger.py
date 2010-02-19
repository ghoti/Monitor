import logging
from config import monitorLog
'''
Created on Dec 3, 2009

@author: ghoti
'''
class logger:
    comlog = logging.getLogger("monitor")
    comlog.setLevel(logging.INFO)
    ch = logging.FileHandler(filename = monitorLog)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    comlog.addHandler(ch)