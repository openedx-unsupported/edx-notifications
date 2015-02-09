i#!/usr/bin/env bash

# this stops the django servers
stopServers() {
    kill $(ps aux | grep "[m]anage.py" | awk '{print $2}')
}

echo "Stop any already running servers..."
stopServers

echo "Starting Notifications Server..."
./manage.py runserver --settings=testserver.settings --noreload &


echo "Waiting for testserver to fully start up..."

until $(curl --output /dev/null --silent --head --fail http://127.0.0.1:8000); do
    printf '.'
    sleep 2
done

echo "Running acceptance tests..."
python bok_choy_tests/test_login.py

# capture the exit code from the test.  Anything more than 0 indicates failed cases.
EXIT_CODE=$?

echo "Shutting down server..."
stopServers

if [[ "$EXIT_CODE" = "0" ]]; then
    echo "All tests passed..."
else
    echo "Failed tests..."
fi
exit $EXIT_CODE
