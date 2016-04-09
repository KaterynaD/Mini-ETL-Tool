cat data/PrioritySLA.csv | psql --host=#host# --port=#RDS.Port# --username=#RDS.MasterUsername# --dbname=#RDS.DBName# --set=ON_ERROR_STOP=true  -c "COPY d_priorities FROM STDIN delimiter ',' csv  quote '\"' header"

