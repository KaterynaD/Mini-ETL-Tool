cat NewData/#table_name#.csv | psql --host=#host# --port=#RDS.Port# --username=#RDS.MasterUsername# --dbname=#RDS.DBName# --set=ON_ERROR_STOP=true  -c "COPY #table_name# FROM STDIN delimiter ',' csv  quote '\"'"

