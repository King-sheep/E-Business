# @Author=Sheep Wang
# @File=config_mysql_db_control.py
# @Created=2026-08-09 11:51
# @Description=config_mysql_db_control.py


import os




# Config DB imformation, 
# load the environment variables first; 
# fall back to local default configurations if they are not set.
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "SheepWang123456@")
MYSQL_DB = os.getenv("MYSQL_DB", "test_db")
MYSQL_CHARSET = "utf8mb4"
