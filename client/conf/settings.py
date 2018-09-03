host = "127.0.0.1"
port = 9800
receive_bytes = 8192
download_dir = r"D:\download"

import os

if not os.path.exists(download_dir):
    os.mkdir(download_dir)
