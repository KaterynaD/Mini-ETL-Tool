#!/usr/bin/python
import json
import sys
import DataLoad
import time
"""
CLILoadTRun.py - 03.21.16 Kate Drogaieva
This module execs commands from a json file
via DataLoad package
"""
#==============================================================================================================================#
try:
    ScriptLoadFile=sys.argv[1]
except:
    ScriptLoadFile="StagingAreaConditions.json"
try:
    Attempt=sys.argv[2]
except:
    Attempt=1
LogDir="logs/"
ModuleName=sys.argv[0].replace(".py","")
LogFileName=ScriptLoadFile
LogFileName=LogFileName.replace(".json","")
LogFileName=LogFileName.replace("/","_")
Dt=time.strftime("%m%d%Y%H%M%S")
LogFileName="%s%s_%s_exec_%s_%s.log" %(LogDir,ModuleName,LogFileName,Attempt,Dt)
#....................................................................................................................
with open(ScriptLoadFile) as data_file:
    ScriptLoad = json.load(data_file)
sa=DataLoad.DataLoad(tables=ScriptLoad,printrawlogs=False)
sa.run(action="exec", attempt=int(Attempt))
sa.SaveToFileExecutionLog(LogFileName)
sa.PrintExecutionLog()

