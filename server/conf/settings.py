host = "0.0.0.0"
port = 9800
max_queue_size = 5
receive_bytes = 8192


import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
account_db_dir = os.path.join(BASE_PATH, "server/db")
ftp_home_dir = os.path.join(BASE_PATH, "server/FTP_DATA")

if not os.path.exists(ftp_home_dir):
    os.mkdir(ftp_home_dir)
if not os.path.exists(account_db_dir):
    os.mkdir(account_db_dir)
