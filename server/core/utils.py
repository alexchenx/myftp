import hashlib
import json
import os

from server.conf import settings


def get_user_data(username):
    path = "%s/%s.json" % (settings.account_db_dir, username)
    user_path = os.path.normpath(path)
    with open(user_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def save_user_data(user_dict):
    path = "%s/%s.json" % (settings.account_db_dir, user_dict["username"])
    user_path = os.path.normpath(path)
    with open(user_path, "w", encoding="utf-8") as f:
        json.dump(user_dict, f)


def md5(content):
    ha = hashlib.md5()
    ha.update(bytes(content, encoding="utf-8"))
    md5_value = ha.hexdigest()
    return md5_value