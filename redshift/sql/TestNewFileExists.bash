#!/bin/bash
[ ! -f NewData/analysts.csv ] && exit 1
[ ! -f NewData/cases.csv ] && exit 1
[ ! -f NewData/logs.csv ] && exit 1
aws s3 ls s3://kdsupportdatanew
if [[ $? -ne 0 ]] ; then
aws s3api create-bucket --bucket kdsupportdatanew --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
if [[ $? -ne 0 ]] ; then
    exit 1
fi
fi
aws s3 cp NewData s3://kdsupportdatanew --recursive
if [[ $? -ne 0 ]] ; then
    exit 1
fi
exit 0




