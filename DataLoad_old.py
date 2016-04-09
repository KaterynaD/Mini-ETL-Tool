#!/usr/bin/python
import os.path
import yaml
import subprocess
import threading
import Queue
import time
"""
DataLoad.py - 03.14.16 Kate Drogaieva
This module provides a class to perform a database table related actions: "create","delete","load","drop" from SQLs in files
v2 03.21.16
"""
class DataLoad(object):
    """
    Performs DB Tables related actions: "create","delete","load","drop" from SQLs in files
    The tables, SQL file names, onError and onSuccess actions, placeholders are described in JSON format
    {
    "Tables":
    [ {"name" : "d_analysts",
        "description" : "SCD type 2",
        "scripts" : {"create" : "sql/create_d_analysts.sql",
                    "load" : "sql/build_scdt2_d_analysts.sql",
                    "drop" : "sql/drop_table.sql"}},
        {"name" : "f_cases",
        "description" : "cases fact table",
        "scripts" : {"create" : "sql/create_f_cases.sql",
                    "load" : "sql/insert_f_cases.sql",
                    "drop" : "sql/drop_table.sql"}},
        {"name": "logs",
        "description": "cases logs",
        "scripts": {
            "create": {
                "file": "mysql/create_logs.sql"
            },
            "load": {
                "file": "mysql/copy_data.sql",
                "OnError": {
                    "could not be read": [
                        "echo './LoadTRun.py StagingArea.json load logs 2 >StagingArea_load_logs_2.log' |at now + 1min",
                        "echo './LoadTRun.py StagingArea.json load logs 3 >StagingArea_load_logs_3.log' |at now + 2min",
                        "Ignore"
                    ]
                },
                "OnSuccess": "./SendToQueue.py ProjectResources.yml LogsAreReady"
            },
            "drop": {
                "file": "mysql/drop_table.sql"
            }
        }
    }
    ],
    "OnError": {
        "1051": [
            "Ignore"
        ],
        "AnyOther": [
            "Stop"
        ]
    },
    "OnSuccess": "./SendToQueue.py ProjectResources.yml DataAreReady",
    "Mode": "Parallel",
    "Placeholders" :
    [
    {"name": "#bucket#",
    "value":"kdsupportdata"}
    ]
    }
    Example an SQL with a parameter

    copy #table_name# from "s3://#bucket#/#table_name#"
    credentials "aws_access_key_id=#aws_access_key_id#;aws_secret_access_key=#aws_secret_access_key#"
    delimiter "," region "us-west-2" REMOVEQUOTES;

    By default #table_name# is replaced with a table name from Tables section and there is no need to describe it in Placeholders section
    Resources yml file keys can be used as a placeholders as well up to 3rd level in a form: #level1.level2.level3#
    Temporary AWS AccessKeyId, SecretAccessKey, Session Token can be sent directly to the specifc Redshift class init
    """

#---------------------------------------------------------------------------------------------
    def __init__(self,tables,connections,resources=None):
        """
            set tables from a json (tables),
            list of connections connected to a database,
            additional parameters from a YAML project configuration file (resources)
        """
        self.tables=tables
        self.connections=connections
        self.connections_num=len(self.connections)
        try:
            self.Mode=self.tables["Mode"]
        except KeyError:
            self.Mode="Sequential"
        try:
            self.tables_num=len(self.tables["Tables"])
        except KeyError:
            self.tables_num=0
        try:
            self.par_num=len(self.tables["Placeholders"])
        except KeyError:
            self.par_num=0
        if resources:
            try:
                with open(resources, "r") as f:
                    self.res = yaml.load(f)
                #resource file flattening
                self.res_params=self.getpar(self.res)
            except KeyError or IOError:
                self.res_params={}
        self.ExecutionLog=[]
#---------------------------------------------------------------------------------------------
    def getpar (self,d,prev_key="",fd={}):
        """
        d is a resource file content where each member can be a dictionary, list or string
        The function flattens it to a dictionary (fd) with "level1.level2.level3":"value" structure
        if an element is a list then the key will look like "level1.listlevel[index].level3"
        This is a recursive function and for inner levels it takes a previous key name and a previous flatten dictionary content
        """
        for key in d:
            if type(d[key]) is str:
                fd[prev_key+key]=d[key]
            elif type(d[key]) is dict:
                self.getpar(d[key],prev_key+key+".",fd)
            elif type(d[key]) is list:
                for i in xrange(len(d[key])):
                    self.getpar(d[key][i],prev_key+key+"["+str(i)+"]"+".",fd)
        return fd
#---------------------------------------------------------------------------------------------
    def replace_Placeholders(self,sql,table_name):
        """
            Replaces Placeholders in SQL text
        """
        #all Placeholders are in ##
        #default #table_name# is replaced with self.tables["Tables"][i]["name"]
        #optional resource file is used to replace #key# from resource file placeholders
        sql=sql.replace("#table_name#",table_name)
        try:
            for par in self.tables["Placeholders"]:
                old = par["name"]
                new = par["value"]
                sql=sql.replace(old,new)
            if self.res_params:
                for key in self.res_params:
                    old = "#"+key+"#"
                    new = self.res_params[key]
                    sql=sql.replace(old,new)
        except KeyError:
            pass
        return sql
#---------------------------------------------------------------------------------------------
    def ActionOnSuccess(self,TableName, Action):
        """
            Runs subprocess.call for an action (string) from json file
            and adds a log record
        """
        self.ExecutionLogAdd (TableName,7,"Run the command onSuccess: ")
        self.ExecutionLogAdd (TableName,8,Action)
        subprocess.call(Action,shell=True)
#---------------------------------------------------------------------------------------------
    def ActionOnError(self,table,action,attempt,e):
        """
            Performs an action (subprocess.call) on an error e (string)
            for a failed action and table
            on the level of a table action, table
            or all tables level
        """
        #.................................................................................................
        def GetAction (OnErrorActions):
            a=None
            for key in OnErrorActions.keys():
                if key in e:
                    try:
                        a=OnErrorActions[key][attempt-1]
                    except IndexError: #if attempt number is more the OnError actions defined, then stop
                        a="Stop"
                    break
            #if action is still not defined, check "AnyOther" key
            if not(a):
                try:
                    a=OnErrorActions["AnyOther"][attempt-1]
                except IndexError: #if attempt number is more the OnError actions defined, then stop
                    a="Stop"
                except KeyError: #if no AnyOther actions then check the other levels
                    a=None
            return a
        #.................................................................................................
        #Priority 1 - table,action
        try:
            OnErrorActions=table["scripts"][action]["OnError"]
            Action=GetAction(OnErrorActions)
        except KeyError:
            Action=None
        if not(Action): #Priority 2 - table
            try:
                OnErrorActions=table["OnError"]
                Action=GetAction(table["OnError"])
            except KeyError:
                Action=None
        if not(Action): #Priority 3 - all tables level
            try:
                OnErrorActions=self.tables["OnError"]
                Action=GetAction(OnErrorActions)
            except KeyError:
                Action="Stop"
        if Action=="Stop":
            return 0
        elif Action=="Ignore":
            return 1
        else:
            #try to run a command
            self.ExecutionLogAdd (table["name"],10,"Run the command: ")
            self.ExecutionLogAdd (table["name"],11,Action)
            subprocess.call([Action],shell=True)
            return 2
#---------------------------------------------------------------------------------------------
    def execute(self,conn,cur,table,action,attempt=1,queue=None,ExecSQLFunc=None):
        """
            Runs SQL e.g. performs action (create, delete, drop or load)  using conn (connection, already connected to a database),
            cur (cursor), table (a structure from JSON file with definition of the action to run, what to do on error or success).
            In a case of a error the action can be repeated via onError command and send attempt (integer)
            queue is used for a parallel execution to return the exit code back to the main thread
        """
        script=table["scripts"][action]["file"]
        self.ExecutionLogAdd (table["name"],1,"====================================")
        if os.path.exists(script):
            sql=self.replace_Placeholders(open(script, "r").read(),table["name"])
            self.ExecutionLogAdd (table["name"],2,"Action: %s for %s from %s" %(action,table["name"],script))
            self.ExecutionLogAdd (table["name"],3,"................................")
            self.ExecutionLogAdd (table["name"],4,sql)
            self.ExecutionLogAdd (table["name"],5,"................................")
            error_f=0
            try:
                if ExecSQLFunc:
                    ExecSQLFunc(sql,cur)
                else:
                    cur.execute(sql)
                conn.commit()
                self.ExecutionLogAdd (table["name"],6,"Done")
                #Trying to run onSuccess action
                try:
                    OnSuccessAction=table["scripts"][action]["OnSuccess"]
                    self.ActionOnSuccess(table["name"],OnSuccessAction)
                except KeyError: #no onSuccess action is configured
                    pass
            except Exception as e:
                self.ExecutionLogAdd (table["name"],9,"Error performing %s for %s using %s"%(action,table["name"],script))
                self.ExecutionLogAdd (table["name"],10,str(e))
                error_f=1
                try:
                    conn.rollback()
                except:
                    self.ExecutionLogAdd (table["name"],11,"Something is really wrong: %s"%str(e))
                OnError=self.ActionOnError(table,action,attempt,str(e))
                if OnError==0:
                    self.ExecutionLogAdd (table["name"],14,"Stop on error")
                elif OnError==1:
                    self.ExecutionLogAdd (table["name"],15,"Error is ignored...Continue")
                    error_f=0
                else:
                    self.ExecutionLogAdd (table["name"],16,"Other action was performed on the error...Stop")
            finally:
                if cur:
                    cur.close()
        else:
            self.ExecutionLogAdd (table["name"],17,"Cannot perform %s for %s using %s Script does not exist"%(action,table["name"],script))
            error_f=1
        self.ExecutionLogAdd (table["name"],18,"====================================")
        if queue:
            queue.put(error_f)
        return error_f
#---------------------------------------------------------------------------------------------
    def run(self,action,StartingTable=None,attempt=1,ExecSQLFunc=None):
        """
        Orginizes sequential or parallel execution of action (create, delete, drop or load) from a first (StartingTable=None)
        or StartingTable (string).
        In a case of a error the action can be repeated via onError command and send attempt (integer)
        """
        def GetTableIndex(TableName):
            Ind=0 #if a given table name is not in the list just start from the first one
            if TableName:
                for j in range(self.tables_num):
                    if self.tables["Tables"][j]["name"]==TableName:
                        Ind=j
                        break
            return Ind
        if action not in ["create","delete","load","drop"]:
            raise ValueError("Can not perform %" %action)
        TotalResult=0
        if self.Mode=="Parallel":
            i=GetTableIndex(StartingTable)
            while i<self.tables_num: #we need to execute action for each table
                Threads=[]
                queue = Queue.Queue()
                j=0
                while (j<self.connections_num
                  and i<self.tables_num):
                #but the number of provided connections can be less then the number of tables
                    table=self.tables["Tables"][i]
                    try:
                        s=table["scripts"][action]
                    except KeyError: #skip this table if there is no action defined
                        i+=1
                        continue
                    cur = self.connections[j].cursor()
                    t = threading.Thread(target=self.execute, args=(self.connections[j],cur,table,action,attempt, queue,ExecSQLFunc,))
                    Threads.append(t)
                    i+=1
                    j+=1
                    if StartingTable: #for a parallel mode we execute the action for only one failed table
                        i=self.tables_num
                        break
                #if we have the same number of connections and tables we will end the inner loop and then outer loop
                #if we have less table then connections  we will end the inner loop and then outer loop
                #if we have more table then connections we will start over in the outer loop
                #the connections are free at the end of the execute
                for t in Threads:
                    t.start()
                for t in Threads:
                    t.join()
                while not queue.empty():
                    TotalResult=TotalResult+int(queue.get())
        else: #default Sequential mode
            StartInd=GetTableIndex(StartingTable)
            for i in range(StartInd,self.tables_num):
                table=self.tables["Tables"][i]
                try:
                    s=table["scripts"][action]
                except KeyError: #skip this table if there is no action defined
                    continue
                cur = self.connections[0].cursor()
                result=self.execute(self.connections[0],cur,table,action,attempt,None,ExecSQLFunc)
                TotalResult=TotalResult+result
                if result==1:
                    break
        if TotalResult==0:
            #Trying to run onSuccess action
            try:
                OnSuccessAction=self.tables["OnSuccess"]
                self.ActionOnSuccess("ZZZZZZZZZZ",OnSuccessAction)
            except KeyError: #no onSuccess action is configured
                pass
        return TotalResult
#---------------------------------------------------------------------------------------------
    def ExecutionLogAdd(self,TableName,Num,Action):
        """
            Adds a record to the log list
            TableName (string) and Num (integer) are used to orginized
            the log by table and in a proper order in a case of the parallel execution
        """
        self.ExecutionLog.append([TableName,Num,time.strftime("%m-%d-%Y %H:%M:%S"),Action])
#---------------------------------------------------------------------------------------------
    def PrintExecutionLog(self):
        """
            Prints the log
        """
        self.ExecutionLog=sorted(self.ExecutionLog, key = lambda x: (x[0], x[1]))
        for log in self.ExecutionLog:
            print log[3]
#---------------------------------------------------------------------------------------------
    def SaveToFileExecutionLog(self,filename):
        """
            Saves the log to a provided filename (string)
        """
        self.ExecutionLog=sorted(self.ExecutionLog, key = lambda x: (x[0], x[1]))
        with open(filename, "w") as f:
            for log in self.ExecutionLog:
                f.write( '%s %s\n' %(log[2],log[3]))
#---------------------------------------------------------------------------------------------
class RedshiftLoad(DataLoad):
    """
        RedshiftLoad class allows providing temporary access credentials to S3 buckets
        to be embeded in Load SQLs
    """
#---------------------------------------------------------------------------------------------
    def __init__(self,tables,connections,resources,bucket_access):
        """
            initis temporary access crdentials to S3 buckets in addition to other parameters
            If they are temporary access crdentials and can not be found in the resource file
        """
        DataLoad.__init__(self,tables,connections,resources)
        self.bucket_access=bucket_access
#---------------------------------------------------------------------------------------------
    def replace_Placeholders(self,sql,table_name):
        """
            Replaces Placeholders in SQL text
            including S3 buckets access specific in Redshift Load
        """
        sql=DataLoad.replace_Placeholders(self,sql,table_name)
        #AccessKeyId, SecretAccessKey, Session Token to access S3 buckets
        sql=sql.replace("#aws_access_key_id#",self.bucket_access["AccessKeyId"])
        sql=sql.replace("#aws_secret_access_key#",self.bucket_access["SecretAccessKey"])
        sql=sql.replace("#aws_session_token#",self.bucket_access["SessionToken"])
        return sql

