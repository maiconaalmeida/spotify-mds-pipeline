@echo off
echo Corrigindo requirements.txt...

(
echo # Core Data Processing
echo pandas^>=2.0.0
echo numpy^>=1.24.0
echo.
echo # Databases
echo mysql-connector-python^>=8.0.0
echo snowflake-connector-python^>=3.0.0
echo.
echo # Kafka
echo confluent-kafka^>=2.0.0
echo kafka-python^>=2.0.0
echo.
echo # AWS ^& Storage
echo boto3^>=1.26.0
echo minio^>=7.0.0
echo.
echo # DBT
echo dbt-core^>=1.5.0
echo dbt-snowflake^>=1.5.0
echo.
echo # Utilities
echo python-dotenv^>=1.0.0
echo psutil^>=5.9.0
echo requests^>=2.28.0
echo python-dateutil^>=2.8.0
) > requirements.txt

echo Requirements.txt corrigido com sucesso!
echo.
echo Para instalar: pip install -r requirements.txt