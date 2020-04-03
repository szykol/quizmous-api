python -m coverage erase
PYTHONPATH=src python -m coverage run --source=src src/main.py & > /dev/null 2>&1 
SERVER_PID=$!
API_TEST="coverage" pytest test/endtoend.py > /dev/null 2>&1
kill $SERVER_PID
echo "Results for end to end tests"
python -m coverage report
python -m coverage run --source=src -m pytest test/unittests.py > /dev/null 2>&1
echo ""
echo "Results for unit tests"
python -m coverage report


PYTHONPATH=src python -m coverage run --source=src src/main.py & > /dev/null 2>&1 
SERVER_PID=$!
API_TEST="coverage" pytest test/endtoend.py > /dev/null 2>&1
kill $SERVER_PID
python -m coverage run --source=src -m -a pytest test/unittests.py > /dev/null 2>&1
echo ""
echo "Results combined"
python -m coverage report
