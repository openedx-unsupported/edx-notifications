#!/bin/bash bash

#setup the log directory variables
export LOG_DIR=testserver/test/acceptance/logs
export SCREENSHOT_DIR=$LOG_DIR
export SELENIUM_DRIVER_LOG_DIR=$LOG_DIR

# Create logs folder in above directory if not already present
# and if there are any existing files in this folder delete these
mkdir -p $LOG_DIR
rm -rf $LOG_DIR/*

# this stops the django servers
stopServers() {
    kill $(ps aux | grep "[m]anage.py" | awk '{print $2}')
}

echo "Stop any already running servers..."
stopServers

echo "Deleting test db if present..."
if [ -f ./test_notifications.db ]; then
    rm ./test_notifications.db
else
    echo "No existing test db file found"
fi

echo "Migrate data"
./manage.py migrate --noinput --settings=testserver.bokchoy_settings

echo "Starting notifications server..."
./manage.py runserver --settings=testserver.bokchoy_settings --noreload &


echo "Waiting for testserver to fully start up..."
until $(curl --output /dev/null --silent --head --fail http://127.0.0.1:8000); do
    printf '.'
    sleep 2
done

#If an individual test name is passed from command prompt run only this test
#otherwise execute all tests
echo "Running acceptance tests..."
if [ "$1" != "" ]; then
    nosetests testserver/test/acceptance/test_notifications.py:TestAddNotifications.$1
else
    nosetests testserver/test/acceptance
fi

# capture the exit code from the test.  Anything more than 0 indicates failed cases.
EXIT_CODE=$?

echo "Shutting down server..."
stopServers

echo "Deleting test db file ..."
rm ./test_notifications.db

if [[ "$EXIT_CODE" = "0" ]]; then
    echo "All tests passed..."
else
    echo "Failed tests..."
fi
exit ${EXIT_CODE}
