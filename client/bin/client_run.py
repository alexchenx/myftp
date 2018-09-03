import os
import sys

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_PATH)

from client.core import main

if __name__ == '__main__':
    client = main.FTPClient()
    client.run()
