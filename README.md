<H1>Mini ETL tool</H1>

<p>DataLoad class (DataLoad.py module) is the core of the tool. The class runs SQL or CLI commands from a JSON object 
in parallel or sequntial mode. If there are placeholders in the command, the tool replaces them from a parameters section of the JSON object,
using a yaml resource file or a dictionary with run-time parameters. Besides the base command, the class runs onSuccess 
or onError actions, sends notificstions onSuccess or onError events. 
Using onSuccess and onError interface you can set up preconditions and a chain of actions to re-start your jobs 
in a case of a failure. 

<p>It does not depend on a specific driver to connect to a database. In a wrapper program you provide one or more connections 
to a database. If the actions in your JSON file are independant, you can use a parallel mode and the number of the threads 
depends on the number of connections you send to the tool.

<p>Connections is an optional parameter in the class and you can omit it if your actions are CLI commands.

<p>Any action can be configured in the JSON object. Only 2 have a special meaning for the tool: "exec" runs a CLI command,
"extract" runs fetch after a cursor execution. 

<p>You can overwrite the tool cursor execute, fetch or subprocess call commands with your own python functions

<p>The class keeps the logs and you can print them or save in a file etc

<H1>Installation</H1>

<p><b><i>The tool itself does not require a specific installation or drivers. It uses only standard Python modules.</b></i> 

<p>However to run the usage examples you need boto3, psycopg2, mysql.connector
boto3 and AWS resources are used just to demo the tool. It can run with traditional database installations, emails and file systems.

<H1>Usage</H1>

<p>There are 4 wrapper programs to demo the tool:

<ol>
<li>MySQLLoadT.py is used to connect to MySQL database using a connection pool if it's possible to run SQLs in parallel.
It works for MariaDB as well
<li>PostgresLoadT.py is used to connect to PostgreSQL database using a connection pool if it's possible
<li>RedshiftLoadT.py is used to connect and run SQLs in Amazon Redshift
<li>CLILoadT.py is used to run only CLI commands and does no require any database connections
</ol>

<p>As a demo case I use a data warehouse project developed for a Support department.
The idea is to estimate performance of support analysts individually and as a team for period of times.
The design is the same in MySQL, PostgreSQL and Redshift in general. The implementation is slightly different in each database.

<p>There are 2 main steps in the project
<ol>
<li>Initial creation and load of the datawarehose with historical data
<li>Periodic updates of the data warehouse with the new data
</ol>

The third step is an extract of the report data in a file.

<H2>Initial creation and load</H2>

<p>The project is started from this command:

<p><i>./CLILoadT.py database/StagingAreaConditions.json</i>

<p>where database is mysql or postgres or redshift

<p>StagingAreaConditions.json file runs a script file to check if the historical data exist. If yes, the file has a configuration to run
immediately <i>./databaseLoadT database/database.yml database/StagingArea.json drop</i> command and send a notification to AWS SNS.
If there are no files in place, the command fails and onError event re-start CLILoadT with the same json files 3 times to wait
till the data will be added in a specific directory. On the 4th time, the load is stopped.

<p>In addition, Redshift script creates an S3 bucket and copies the files

<p>StagingArea.json file has instruction to run itself for create and then load if each previous action is successfull. When the load of
the staging area is done, SupportDW.json file is started in the same way from onSuccessload key in StagingArea.json

<p>Depends on the database, the scripts create stored procedures and run them or run anonymous blocks.

<p>MySQLLoadT.py replaces the tool function to run more then one SQL command in one execute Python command.

<p>MySQLLoadT.py and PostgresLoadT.py replaces the tool function to run stored procedures.

<p>RedshiftLoadT.py uses temporary access crdentials to access S3 buckets with the data and sends them in the tool in run-time dictionary
to replace placeholders in SQL commands

<p>PostgresLoadT.py uses CLI command to load the data and connects to the database from the command. It uses a resource file 
to replace placeholders in the command connection string.

<H2>Periodic updates of the data warehouse with the new data</H2>

<p>The process is almost the same except the drop stage. 

<p>The first action (checking if new export files exist) can be scheduled for the periodic updates of the data warehouse. The 
consiquent actions will be run from the first action by itself.

<p>JSON files used in the periodic update actions: StagingAreaConditionsNewData.json->NewDataForLoad.json->SupportDW_NewData.json

<H2>Extract report</H2>

<p>TeamPerformanceReport.json is used to run a report and save data to a file.
<p>MySQL and PostgreSQL process uses Fetch python command and save the data to a text file. The JSON file provides 
the export file parameters: filename, delimeter, quotes, lineterminator etc
<p>Redshift process unloads data to a bucket first and then copies the file to a file system

<H2>AWS usage notes</H2>

<p>I use AWS RDS databses and Redshift in a Free Tier AWS account and to save free hours do not keep them up and running when 
I do not work on the project. So I build them only when I need them and delete when I'm done with the project.

<p>Here are the modules I use for this purpose:
<ol>
<li>RedshiftUtility.py is used to build or delete Redshift cluster
<li>RDSUtility.py is used to build or delete an RDS database
<li>VPCUtility.py builds VPC and allows you to build an RDS or Redshift in a VPC
</ol>

<p>YAML resource files are used to create a database or cluster. LoadT.py modules use the above packages and the correspondent classes 
to get endpoints of the resources based on the known names in YAML resources in order to connect.

<p>To send notifications onSuccess or onError I use AWS SNS or SQS services. These modules are used to communicate with AWS resources:

<ol>
<li>SNSUtility.py is used to create, delete, post a message to an SNS topic
<li>SQSUtility.py is used to create, delete, post or retrieve a message to/from a queue
<li>SendToETLSNS.py is used to send a message from a command line to a predefine "ETL" topic
<li>SendToQueue.py is used to send a message from a command line to a predefine "ETL" queue
</ol>


<H2>Support Department Data Warehouse</H2>

<p>The star schema is populated with a sample data set. It includes: <i>Slowly Changing Dimension type 2, 
Flatten hierarchy dimension, calendar dimension, a fact table</i>. 


<p><b>Source Data</b>: Analysts table is from an HR system current data and historical data from files, Cases, Products tables and a text Logs file are from a Support application,  Support department  provided a small Excel file with SLA per cases priority. 
The data used in the project are fabricated, test data. For simplicity I do not include some details which usually you can find in this kind of data (Case Subject, analysts emails etc) if they are not used to calculate analysts performance KPIs. The data for Calendar dimension is usally built in an Excel by business with important companies holiday's fiscal year data etc.  
Please see SourceDataERD.jpg and StarSchema.jpg for details regarding each table

<p>Transformation to Star Schema:
<ol>
<li>Analysts: Analysts can change their names, add more skills in profiles and move between teams. Support department needs to analyze performance by team so they keep track of such movements between the teams for years and provided the data to build the data warehouse analysts table. Slowly Changing Dimension Type 2 will be used in the data warehouse for D_Analysts dimension. We need a surragate key (id) in this dimension, Start Date and End Date when an analysts was in a specific team and isActiveFlag to simplify queries. There was also to request from Support department to track skills changes for a future analysis. We do not track changes in the names because the changes are not relevant to the project purpose. See transformation SQLs in sql/build_scdt2_d_analysts.sql for the initial load and sql/merge_scdt2_d_analysts for a periodic update.
<li>Products: The table consists from Product Lines, Product groups and Products. There is parent-child relationship in the table. The cases can be created only for the product level. To be used in BI tools the data have to be flatten in D_Products dimension. Analyze by product is not the main goal of the demo project so let's assume there is no changes in the set of products since it was originally built and flatten in 3 columns (ProductLine, ProductGroup and Product). The garnularity of the dimension is Product now. See sql/flatten_hierar_d_products.sql
<li>Priority: The SLAs are the same for each years of data but can be changed in a future. We can build Slowly Changing Dimension Type 1 using additional columns for changes and adjust the reporting queries. The change is a simple and  rare event, and I do not include a specific code in the project
<li>Calendar: The PK of the dimension is in the form YYYYMMDD and the granularity is a day We need hours or even seconds to analyze analysts performance as a difference between 2 datetimes in logs. However we do not need to analyze it for each hour. If we should we would add one more time dimension.
<li>Cases and Logs: These 2 data sources are used to build F_Cases fact tables. Assign, Response and Resolve KPIs are calculated as a difference between event times in the logs. The facts are AssignDT, ResponseDT and ResolveDT datetimes extracted from the logs and assigned to each case. The rest of the columns in the fact tables are FK to dimensions. Analyst_Id is a FK to D_Analysts and it's a surrogate keep. There is also natural key (aid) in the table to demo the same analyst (with the same aid) can be related to different cases with different surrogate keys in different times of his professional life. There are pairs of similar column names in the table: CreatedDt_id and CreatedDate, AssignedDt_id and AssignedDate etc. The first one (_id) is a FK to D_Calendar and has integer type and YYYYMMDD format. We need it to analyze performance by period of times. The other one is a datetime column and it's fact in the fact table. We use it to calculate performance KPIs. See sql/create_f_cases.sql for each column comment and transformations in sql/insert_f_cases.sql and sql/merge_f_cases.sql
</ol>

<p>We do not want to have outer joins in our BI queries and to achieve this I add -1 id default values in each dimensional table. Fact table FK columns uses -1 in a case a dimensional value is unknown instead of null.
Example: a case can be created but at the moment of the data warehouse load not assigned to an analyst. The case will have -1 in analyst id as well as assigneddt_id, responsedt_id, resolvedt_id





