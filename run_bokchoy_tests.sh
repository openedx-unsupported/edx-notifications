#!/bin/bash bash


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

echo "Creating new test db and sync data..."
./manage.py syncdb --noinput --settings=testserver.bokchoy_settings

ech "Migrate data"
./manage.py migrate --noinput --settings=testserver.bokchoy_settings

echo "Starting notifications server..."
./manage.py runserver --settings=testserver.bokchoy_settings --noreload &


echo "Waiting for testserver to fully start up..."
until $(curl --output /dev/null --silent --head --fail http://127.0.0.1:8000); do
    printf '.'
    sleep 2
done

echo "Running acceptance tests..."
nosetests testserver/test/acceptance

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