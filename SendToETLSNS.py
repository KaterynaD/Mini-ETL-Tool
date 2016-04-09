#!/usr/bin/python
import SNSUtility
import sys

MyTopic=SNSUtility.SNSUtility(TopicName="ETL")
response=MyTopic.TopicPublish(sys.argv[1],sys.argv[2])
