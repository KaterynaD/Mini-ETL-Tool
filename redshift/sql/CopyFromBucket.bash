#!/bin/bash
aws s3 cp s3://#bucket#/TeamPerformanceRedshift000 reports/TeamPerformanceRedshift.csv
if [[ $? -ne 0 ]] ; then
    exit 1
fi
exit 0
