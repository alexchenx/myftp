host = "127.0.0.1"
port = 9800
receive_bytes = 8192

import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
download_dir = os.path.join(BASE_PATH, "download")
if not os.path.exists(download_dir):
    os.mkdir(download_dir)
