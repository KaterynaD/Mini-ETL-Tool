#!/bin/bash
[ ! -f data/analysts_2010.csv ] && exit 1
[ ! -f data/analysts_2011.csv ] && exit 1
[ ! -f data/analysts_2012.csv ] && exit 1
[ ! -f data/analysts_2013.csv ] && exit 1
[ ! -f data/analysts_2014.csv ] && exit 1
[ ! -f data/calendar.csv ] && exit 1
[ ! -f data/cases_2011.csv ] && exit 1
[ ! -f data/cases_2012.csv ] && exit 1
[ ! -f data/cases_2013.csv ] && exit 1
[ ! -f data/cases_2014.csv ] && exit 1
[ ! -f data/logs_2011.csv ] && exit 1
[ ! -f data/logs_2012.csv ] && exit 1
[ ! -f data/logs_2013.csv ] && exit 1
[ ! -f data/logs_2014.csv ] && exit 1
[ ! -f data/PrioritySLA.csv ] && exit 1
[ ! -f data/products.csv ] && exit 1
aws s3 ls s3://kdsupportdata
if [[ $? -ne 0 ]] ; then
aws s3api create-bucket --bucket kdsupportdata --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
if [[ $? -ne 0 ]] ; then
    exit 1
fi
fi
aws s3 cp data s3://kdsupportdata --recursive
if [[ $? -ne 0 ]] ; then
    exit 1
fi
exit 0
