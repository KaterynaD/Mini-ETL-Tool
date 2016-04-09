#!/usr/bin/python
import mysql.connector
import mysql.connector.pooling
import yaml
import json
import sys
import DataLoad
import RDSUtility
import time
"""
LoadTRun.py - 03.21.16 Kate Drogaieva
This module connects to a MySQL or MariaDB database
then loads data into staging area tables or transform them to a star schema
"""
#---------------------------------------------------------------------------------
def ExecSQL(sql,cur):
    for result in cur.execute(sql,multi = True):
        pass
#---------------------------------------------------------------------------------
def ExecProc(sql,cur):
    cur.callproc(str(sql))
#---------------------------------------------------------------------------------
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
with open(ResourceFile, "r") as f:
    res = yaml.load(f)
#....................................................................................................................
LogDir="logs/"
ModuleName=sys.argv[0].replace(".py","")
LogFileName=ScriptLoadFile
LogFileName=LogFileName.replace(".json","")
LogFileName=LogFileName.replace("/","_")
Dt=time.strftime("%m%d%Y%H%M%S")
LogFileName="%s%s_%s_%s_%s_%s.log" %(LogDir,ModuleName,LogFileName,Action,Attempt,Dt)
#....................................................................................................................
print "Getting RDS endpoint to connect..."
c=RDSUtility.RDSUtility(ResourceFile)
host=c.endpoint
if not(host):
    sys.exit("MySQL is not available. Stop the program")
else:
    print "MySQL is available at %s" %host
    print "Port: %s" %res["RDS"]["Port"]
#....................................................................................................................
with open(ScriptLoadFile) as data_file:
    ScriptLoad = json.load(data_file)
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
        conn_pool = mysql.connector.pooling.MySQLConnectionPool(user=res["RDS"]["MasterUsername"],
                              password=res["RDS"]["MasterUserPassword"],
                              host=host,
                              port=res["RDS"]["Port"],
                              database=res["RDS"]["DBName"],
                              pool_name = "mypool",
                              pool_size = pool_size)
        for i in xrange(0,pool_size):
            conn.append(conn_pool.get_connection())
    else:
        #just one connection for sequential mode
        conn.append(mysql.connector.connect(user=res["RDS"]["MasterUsername"],
                              password=res["RDS"]["MasterUserPassword"],
                              host=host,
                              port=res["RDS"]["Port"],
                              database=res["RDS"]["DBName"]))
    sa=DataLoad.DataLoad(ScriptLoad,conn,ResourceFile,printrawlogs=False)
    if "SupportDW_NewData.json" in ScriptLoadFile:
        sa.run(Action,Table,int(Attempt),ExecProc)
    else:
        sa.run(Action,Table,int(Attempt),ExecSQL)
    sa.SaveToFileExecutionLog(LogFileName)
    sa.PrintExecutionLog()
except KeyError:
    print "Wrong MySQL connect configuration parameters"
except mysql.connector.Error as err:
    print "Unable to connect to %s" %host
    print("Something went wrong: {}".format(err))
finally:
    if conn:
        for c in conn:
            c.close()

