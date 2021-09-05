import sys

sys.path.append("..")

from azure_main import Azure
from azure_sdk import AzureMySQLManagement, AzureResourceManagement
from config.config import load_env
from config.names import AzureNames

load_env()

LOCATION = "westus"
RULE = "allow_ip"
TABLE = "ExampleTable1"

names = AzureNames(
    resource_group="PythonAzureExample-DB-rg",
)

azure_resource_sdk = AzureResourceManagement()
azure_mysql_sdk = AzureMySQLManagement()

azure_resource = Azure(azure_resource_sdk, names)
azure_mysql = Azure(azure_mysql_sdk, names)

azure_resource.sdk.create_resoruce({"location": LOCATION})

server = azure_mysql.sdk.create_servers(location=LOCATION, version="FIVE7")

print(server.name)

print(f"Provisioned MySQL server {server.name}")

firewall_rule = azure_mysql.sdk.create_firewall_rules(rule=RULE)

print(f"Provisioned firewall rule {firewall_rule.name}")

db = azure_mysql.sdk.create_database({})

print(f"Provisioned MySQL database {db.name} with ID {db.id}")

connection = azure_mysql.sdk.connect_to_database()

cursor = connection.cursor()

sql_create = f"CREATE TABLE {TABLE} (name varchar(255), code int)"

cursor.execute(sql_create)
print(f"Successfully created table {TABLE}")

sql_insert = f"INSERT INTO {TABLE} (name, code) VALUES ('Azure', 1)"
insert_data = "('Azure', 1)"

cursor.execute(sql_insert)
print("Successfully inserted data into table")

sql_select_values = f"SELECT * FROM {TABLE}"

cursor.execute(sql_select_values)
row = cursor.fetchone()

while row:
    print(str(row[0]) + " " + str(row[1]))
    row = cursor.fetchone()

connection.commit()
