import os
import time

DIR_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(DIR_ROOT, 'log', 'run.log')

def logger(log_message):
    global LOG_DIR
    isExists = os.path.exists(LOG_DIR)
    if not isExists:
        f = open(LOG_DIR, 'w')
        f.write("")
        f.close()

    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    f = open(LOG_DIR, 'a')
    f.write(date + '\t' + log_message + '\n')
    f.close()