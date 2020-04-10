python -m coverage erase
python -m coverage run run.py & > /dev/null 2>&1 
SERVER_PID=$!
API_TEST="coverage" python -m pytest test/endtoend/* > /dev/null 2>&1
kill $SERVER_PID
echo "Results for end to end tests"
python -m coverage report
python -m coverage run -m pytest test/* > /dev/null 2>&1
echo ""
echo "Results for unit tests"
python -m coverage report


python -m coverage run run.py & > /dev/null 2>&1 
SERVER_PID=$!
API_TEST="coverage" python -m pytest test/endtoend/* > /dev/null 2>&1
kill $SERVER_PID
python -m coverage run -m -a pytest test/* > /dev/null 2>&1
echo ""
echo "Results combined"
python -m coverage report
