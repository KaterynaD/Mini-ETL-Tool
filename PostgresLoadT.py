#!/usr/bin/python
import psycopg2
import json
import yaml
import RDSUtility
import sys
import DataLoad
import time

"""
PostgresLoadT.py - 04.01.16 Kate Drogaieva
This module connects to a PostgreSQL
then loads data into staging area tables or transform them to a star schema
"""
#---------------------------------------------------------------------------------
def ExecProc(sql,cur):
    cur.callproc(str(sql))
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
#....................................................................................................................

print "Getting PostgreSQL endpoint to connect..."
c=RDSUtility.RDSUtility(ResourceFile)
host=c.endpoint
if not(host):
    sys.exit("PostgreSQL is not available. Stop the program")
with open(ScriptLoadFile) as data_file:
    ScriptLoad = json.load(data_file)
#echo *:*:*:masteruser:Kaktus2015> ~/.pgpass
#chmod 0600 ~/.pgpass
#....................................................................................................................
try:
    Mode=ScriptLoad["Mode"]
except KeyError:
    Mode="Sequential"
#....................................................................................................................
conn=[]
try:
    if Mode=="Parallel":
        #if it's a parallel mode we need a pool of connections Each thread performs the action for each table in parallel
        #if there is a Table in the parameters, in parallel mode we will execute the action only once for the given table only
        if not(Table):
            pool_size=len(ScriptLoad["Tables"])
        else:
            pool_size=1
        for i in xrange(0,pool_size):
                conn.append(psycopg2.connect(
        host=host,
        user=res["RDS"]["MasterUsername"],
        port=res["RDS"]["Port"],
        password=res["RDS"]["MasterUserPassword"],
        dbname=res["RDS"]["DBName"]))
    else:#just one connection for sequential mode
        conn.append(psycopg2.connect(
        host=host,
        user=res["RDS"]["MasterUsername"],
        port=res["RDS"]["Port"],
        password=res["RDS"]["MasterUserPassword"],
        dbname=res["RDS"]["DBName"]))
    RuntimeParams={}
    RuntimeParams["host"]=host
    sa=DataLoad.DataLoad(ScriptLoad,conn,ResourceFile,RunTimeParameters=RuntimeParams)
    if "SupportDW_NewData.json" in ScriptLoadFile:
        sa.run(Action,Table,int(Attempt),ExecProc)
    else:
        sa.run(Action,Table,int(Attempt))
    sa.SaveToFileExecutionLog(LogFileName)

except KeyError:
    print "Wrong PostgreSQL connect configuration parameters"
except psycopg2.Error as e:
    print "Unable to connect to %s" %host
    print e.pgerror
    print e.diag.message_detail
finally:
    if conn:
        for c in conn:
            c.close()

