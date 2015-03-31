import os
import errno

"""
This section is valid only when tests are run from pycharm instead of
running these using shell script
This section will create a logs folder in acceptance directory if it does
not exists
"""
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

"""
If tests are run using shell script the current directory is not acceptance
in this case create logs folder in /testserver/test/acceptance
If tests are run using pycharm the current folder is acceptance
in this case just create logs folder in current directory
"""
if 'acceptance' in os.path.abspath(os.curdir):
    mkdir_p(os.curdir + '/logs')
    os.environ['SCREENSHOT_DIR'] = os.curdir + '/logs'
    os.environ['SELENIUM_DRIVER_LOG_DIR'] = os.curdir + '/logs'
else:
    os.environ['SCREENSHOT_DIR'] = os.curdir + '/testserver/test/acceptance/logs'
    os.environ['SELENIUM_DRIVER_LOG_DIR'] = os.curdir + '/testserver/test/acceptance/logs'

"""
Provide the url and credentials here
"""
base_url = 'http://127.0.0.1:8000/'
user_name = 'testuser1'
user_email = 'testuser1@edx.org'
password = '123'


"""
Define default timeout for waits and promises
"""
default_timeout = 20