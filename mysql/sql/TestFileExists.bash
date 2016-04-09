#!/bin/bash
[ ! -f data/analysts_2010.csv ] && exit 1
[ ! -f data/analysts_2011.csv ] && exit 1
[ ! -f data/analysts_2012.csv ] && exit 1
[ ! -f data/analysts_2013.csv ] && exit 1
[ ! -f data/analysts_2014.csv ] && exit 1
[ ! -f data/calendar.csv ] && exit 1
[ ! -f data/cases.csv ] && exit 1
[ ! -f data/logs.csv ] && exit 1
[ ! -f data/PrioritySLA.csv ] && exit 1
[ ! -f data/products.csv ] && exit 1
exit 0
