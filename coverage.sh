#!/usr/bin/env bash

make testfiles -C test_inputs
coverage run --branch --source TweenSVG -m TestTweenSVG
stat=$?
coverage report -m | tee coveragereport
exit $stat
