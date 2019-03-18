import hashlib
import json
import os

from server.conf import settings


def get_user_data(username):
    '''
    根据用户名获取用户账户信息
    :param username:
    :return:
    '''
    path = "%s/%s.json" % (settings.account_db_dir, username)
    user_path = os.path.normpath(path)
    with open(user_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def save_user_data(user_dict):
    '''
    保存已修改的用户账户信息到用户文件
    :param user_dict:
    :return:
    '''
    path = "%s/%s.json" % (settings.account_db_dir, user_dict["username"])
    user_path = os.path.normpath(path)
    with open(user_path, "w", encoding="utf-8") as f:
        json.dump(user_dict, f)


def md5(content):
    '''
    将传入内容进行md5加密
    :param content:
    :return:
    '''
    ha = hashlib.md5()
    ha.update(bytes(content, encoding="utf-8"))
    md5_value = ha.hexdigest()
    return md5_value
