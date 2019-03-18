host = "0.0.0.0"
port = 9800
receive_bytes = 1024

import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 用户数据存放目录
account_db_dir = os.path.join(BASE_PATH, "server/db")

# 存放用户文件的总home目录
ftp_home_dir = os.path.join(BASE_PATH, "server/FTP_DATA")

# 最大连接数
max_conn_size = 10

if not os.path.exists(ftp_home_dir):
    os.mkdir(ftp_home_dir)
if not os.path.exists(account_db_dir):
    os.mkdir(account_db_dir)
