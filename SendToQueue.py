#!/usr/bin/python
import SQSUtility
import sys
"""
SendToQueue.py - 03.14.16 Kate Drogaieva
The module allows to send a message to DataReadiness queue from a command line
1st argument is the message itself
"""
MyQueue=SQSUtility.SQSUtility(QueueName="DataReadiness")
if not MyQueue.QueueUrl:
    MyQueue.create_queue()
MyQueue.SendMessage(sys.argv[1])
