#!/usr/bin/env bash

coverage run --branch --source TweenSVG -m TestTweenSVG
stat=$?
coverage report -m | tee coveragereport
exit $stat
