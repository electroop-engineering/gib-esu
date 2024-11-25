#!/bin/sh
pytest --junitxml=reports/junit/junit.xml --html=reports/junit/report.html && genbadge tests -o reports/junit/tests-badge.svg
coverage report && coverage xml -o reports/coverage/coverage.xml && coverage html -d reports/coverage && genbadge coverage -o reports/coverage/coverage-badge.svg
flake8 . --exit-zero --format=html --htmldir ./reports/flake8 --statistics --tee --output-file reports/flake8/flake8stats.txt && genbadge flake8 -o reports/flake8/flake8-badge.svg
