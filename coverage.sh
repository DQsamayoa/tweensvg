#!/usr/bin/env bash

coverage run --branch --source TweenSVG -m TestTweenSVG
coverage report -m | tee coveragereport
