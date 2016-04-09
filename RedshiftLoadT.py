#!/usr/bin/python

import psycopg2
import json
import yaml
import RedshiftUtility
import sys
import DataLoad
import boto3
import time
"""
RedshiftLoadT.py - 03.14.16 Kate Drogaieva
This module connects to a Redshift cluster using temporary access credentials
then loads data into staging area tables or transform them to a star schema
"""
#==============================================================================================================================#
try:
    ResourceFile=sys.argv[1]
except:
    ResourceFile="ProjectResources.yml"
try:
    ScriptLoadFile=sys.argv[2]
except:
    ScriptLoadFile="StagingArea.json"
try:
    Action=sys.argv[3]
except:
    Action="drop"
try:
    Table=sys.argv[4]
except:
    Table=None
try:
    Attempt=sys.argv[5]
except:
    Attempt=1
    
LogDir="logs/"
ModuleName=sys.argv[0].replace(".py","")
LogFileName=ScriptLoadFile
LogFileName=LogFileName.replace(".json","")
LogFileName=LogFileName.replace("/","_")
Dt=time.strftime("%m%d%Y%H%M%S")
LogFileName="%s%s_%s_%s_%s_%s.log" %(LogDir,ModuleName,LogFileName,Action,Attempt,Dt)
#....................................................................................................................
    
with open(ResourceFile, "r") as f:
    res = yaml.load(f)

with open(ResourceFile, "r") as f:
    res = yaml.load(f)

print "Granting Temp access to copy data from buckets"
#Temp access to copy data from buckets
client = boto3.client("sts")
response = client.assume_role(
RoleArn=res["Access"]["RoleArn"],
RoleSessionName="DataLoad"
)
Bucket_Access={}
Bucket_Access["aws_access_key_id"]=response["Credentials"]["AccessKeyId"]
Bucket_Access["aws_secret_access_key"]=response["Credentials"]["SecretAccessKey"]
Bucket_Access["aws_session_token"]=response["Credentials"]["SessionToken"]
#....................................................................................................................
print "Getting Redshift endpoint to connect..."
c=RedshiftUtility.RedshiftUtility(ResourceFile)
host=c.endpoint
if not(host):
    sys.exit("Redshift Cluster is not available. Stop the program")
#....................................................................................................................
try:
    conn = psycopg2.connect(
    host=host,
    user=res["RedshiftCluster"]["MasterUsername"],
    port=res["RedshiftCluster"]["Port"],
    password=res["RedshiftCluster"]["MasterUserPassword"],
    dbname=res["RedshiftCluster"]["DBName"])
    with open(ScriptLoadFile) as data_file:
        ScriptLoad = json.load(data_file)
    sa=DataLoad.DataLoad(ScriptLoad,[conn],ResourceFile,RunTimeParameters=Bucket_Access)
    sa.run(Action,Table,int(Attempt))
    sa.SaveToFileExecutionLog(LogFileName)
except KeyError:
    print "Wrong Redshift connect configuration parameters"
except psycopg2.Error as e:
    print "Unable to connect to %s" %host
    print e.pgerror
    print e.diag.message_detail
finally:
    if conn:
        conn.close();

