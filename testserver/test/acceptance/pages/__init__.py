import os
import errno


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

if 'acceptance' in os.path.abspath(os.curdir):
    mkdir_p(os.curdir + '/logs')
    os.environ['SCREENSHOT_DIR'] = os.curdir + '/logs'
    os.environ['SELENIUM_DRIVER_LOG_DIR'] = os.curdir + '/logs'
else:
    os.environ['SCREENSHOT_DIR'] = os.curdir + '/testserver/test/acceptance/logs'
    os.environ['SELENIUM_DRIVER_LOG_DIR'] = os.curdir + '/testserver/test/acceptance/logs'

base_url = 'http://127.0.0.1:8000/'
user_name = 'testuser1'
user_email = 'testuser1@edx.org'
password = 'ARbi12.,'
