#!/bin/bash
aws s3 ls s3://#bucket#
if [[ $? -ne 0 ]] ; then
aws s3api create-bucket --bucket #bucket# --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
if [[ $? -ne 0 ]] ; then
    exit 1
fi
fi
exit 0




