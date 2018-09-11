import socket
import json
import os
import struct
import subprocess
import platform
from server.conf import settings
from server.core import utils


class FTPServer:
    def __init__(self):
        self.user_data = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.platform = None
        if platform.uname()[0] == "Windows":
            self.platform = "Windows"
        else:
            self.platform = "Linux"

    def verify_search_command_parameter(self, cmd_list):
        if len(cmd_list) > 2:
            print("参数太多了，不支持。")
            msg_dict = {
                "msg_type": "error",
                "msg_content": "参数太多了，不支持。"
            }
            self.send_msg_dict(msg_dict)
            return False
        else:
            return True

    def verify_action_command_parameter(self, cmd_list):
        if len(cmd_list) < 2:
            print("缺少参数")
            head_dict = {
                "msg_type": "error",
                "msg_content": "缺少参数"
            }
            self.send_msg_dict(head_dict)
            return False
        else:
            return True

    def execute_command(self, cmd_all):
        print("要执行的命令为：%s" % (cmd_all))
        obj = subprocess.Popen(cmd_all, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = obj.stdout.read()
        stderr = obj.stderr.read()
        msg_dict = {
            "msg_type": "info",
            "msg_size": len(stdout) + len(stderr)
        }
        self.send_msg_dict(msg_dict)
        self.conn.send(stdout)
        self.conn.send(stderr)

    def _ls(self, cmd_list):
        if self.verify_search_command_parameter(cmd_list):
            path = os.path.normpath("%s/%s" % (self.user_data["home"], self.user_data["current_dir"]))
            if len(cmd_list) == 2:
                path = os.path.normpath("%s/%s/%s" % (self.user_data["home"], self.user_data["current_dir"], cmd_list[1]))
            if self.platform == "Windows":
                cmd_all = "dir %s" % (path)
            if self.platform == "Linux":
                cmd_all = "ls -all %s" % (path)
            self.execute_command(cmd_all)

    def _cd(self, cmd_list):
        if self.verify_search_command_parameter(cmd_list):
            path = os.path.normpath(self.user_data["home"])
            if len(cmd_list) == 2:
                if cmd_list[1] == "/" or cmd_list[1] == "\\":
                    path = os.path.normpath(self.user_data["home"])
                else:
                    path = os.path.normpath("%s/%s/%s" % (self.user_data["home"], self.user_data["current_dir"], cmd_list[1]))
            if os.path.isdir(path):
                if self.user_data["home"] not in path:
                    msg_dict = {
                        "msg_type": "info_cd",
                        "msg_content": "已在根目录，不能切换了。",
                        "current_dir": self.user_data["current_dir"]
                    }
                    self.send_msg_dict(msg_dict)
                else:
                    self.user_data["current_dir"] = path.split(self.user_data["home"])[1]
                    msg_dict = {
                        "msg_type": "info_cd",
                        "msg_content": "",
                        "current_dir": self.user_data["current_dir"]
                    }
                    self.send_msg_dict(msg_dict)
            else:
                msg_dict = {
                    "msg_type": "error",
                    "msg_content": "目录不存在"
                }
                self.send_msg_dict(msg_dict)

    def _mkdir(self, cmd_list):
        if self.verify_search_command_parameter(cmd_list) and self.verify_action_command_parameter(cmd_list):
            path = os.path.normpath("%s/%s/%s" % (self.user_data["home"], self.user_data["current_dir"], cmd_list[1]))
            if self.platform == "Windows":
                cmd_all = "mkdir %s" % (path)
            if self.platform == "Linux":
                cmd_all = "mkdir -p %s" % (path)
            self.execute_command(cmd_all)

    def _rmdir(self, cmd_list):
        if self.verify_search_command_parameter(cmd_list) and self.verify_action_command_parameter(cmd_list):
            path = os.path.normpath("%s/%s/%s" % (self.user_data["home"], self.user_data["current_dir"], cmd_list[1]))
            if os.path.isdir(path):
                cmd_all = "rmdir %s" % (path)
                self.execute_command(cmd_all)
            else:
                msg_dict = {
                    "msg_type": "error",
                    "msg_content": "目录不存在"
                }
                self.send_msg_dict(msg_dict)

    def _rm(self, cmd_list):
        if self.verify_search_command_parameter(cmd_list) and self.verify_action_command_parameter(cmd_list):
            path = os.path.normpath("%s/%s/%s" % (self.user_data["home"], self.user_data["current_dir"], cmd_list[1]))
            if os.path.exists(path):
                if not os.path.isdir(path):
                    if self.platform == "Windows":
                        cmd_all = "del /Q %s" % (path)
                    if self.platform == "Linux":
                        cmd_all = "rm -f %s" % (path)
                    path_size = os.path.getsize(path)
                    self.execute_command(cmd_all)
                    if path_size != 0:
                        self.user_data["current_quota"] -= path_size
                        utils.save_user_data(self.user_data)
                else:
                    msg_dict = {
                        "msg_type": "error",
                        "msg_content": "不支持使用此命令删除目录"
                    }
                    self.send_msg_dict(msg_dict)
            else:
                msg_dict = {
                    "msg_type": "error",
                    "msg_content": "文件不存在"
                }
                self.send_msg_dict(msg_dict)

    def _exit(self, cmd_list):
        print("客户端 %s 断开" % self.client_address)
        self.conn.close()

    def _get(self, cmd_list, received_size=0):
        if self.verify_search_command_parameter(cmd_list) and self.verify_action_command_parameter(cmd_list):
            file_path = os.path.normpath("%s/%s/%s" % (self.user_data["home"], self.user_data["current_dir"], cmd_list[1]))
            if received_size != 0:
                file_path = os.path.normpath("%s/%s" % (self.user_data["home"], cmd_list[1]))
            file_name = os.path.basename(file_path)
            print("get 的文件路径为：", file_path)
            absolute_file_path = os.path.normpath("/%s/%s" % (self.user_data["current_dir"], cmd_list[1]))
            print("absolute_file_path:", absolute_file_path)
            if os.path.exists(file_path):
                if not os.path.isdir(file_path):
                    print("检测文件是存在的，开始发送")
                    file_size = os.path.getsize(file_path)
                    head_dict = {
                        "msg_type": "info",
                        "file_name": file_name,
                        "file_size": file_size,
                        "file_md5": utils.md5(file_name),
                        "absolute_file_path": absolute_file_path,
                        "transfer_flag": "",
                        "received_size": received_size
                    }
                    if received_size != 0:
                        head_dict["transfer_flag"] = "continuingly"
                    self.send_msg_dict(head_dict)
                    with open(file_path, "rb") as f:
                        if received_size != 0:
                            f.seek(received_size)
                        for line in f:
                            self.conn.send(line)
                        else:
                            print("发送完成。")
                else:
                    print("目录不能下载")
                    head_dict = {
                        "msg_type": "error",
                        "msg_content": "目录不能下载"
                    }
                    self.send_msg_dict(head_dict)
            else:
                print("文件不存在")
                head_dict = {
                    "msg_type": "error",
                    "msg_content": "文件不存在"
                }
                self.send_msg_dict(head_dict)

    def _put(self, cmd_list, transferred_size=0):
        if self.verify_search_command_parameter(cmd_list) and self.verify_action_command_parameter(cmd_list):
            data_dict = self.receive_msg_dict()
            print("data_dict:", data_dict)
            if data_dict["msg_type"] == "error":
                print(data_dict["msg_content"])
            else:
                file_size = data_dict["file_size"]
                if (file_size + self.user_data["current_quota"]) > self.user_data["quota"]:
                    print("文件太大了，超过磁盘配额，不能上传")
                    head_dict = {
                        "msg_type": "error",
                        "msg_content": "文件太大了，超过磁盘配额，不能上传"
                    }
                    self.send_msg_dict(head_dict)
                else:
                    print("空间足够可以上传")
                    head_dict = {
                        "msg_type": "info",
                        "msg_content": "配额足够，可以上传"
                    }
                    self.send_msg_dict(head_dict)
                    file_name = data_dict["file_name"]
                    file_md5 = data_dict["file_md5"]
                    if transferred_size != 0:
                        mode = "ab"
                        path = os.path.normpath("%s/%s" % (self.user_data["home"], cmd_list[1]))
                    else:
                        mode = "wb"
                        path = os.path.normpath(
                            "%s/%s/%s" % (self.user_data["home"], self.user_data["current_dir"], file_name))

                    with open(path, mode) as f:
                        if transferred_size != 0:
                            f.seek(transferred_size)
                        while transferred_size < file_size:
                            data = self.conn.recv(settings.receive_bytes)
                            if not data:
                                raise Exception("客户端已断开连接！！")
                            f.write(data)
                            transferred_size += len(data)
                        else:
                            print("文件接收完成")
                            if file_md5 == utils.md5(file_name):
                                print("文件校验正确")
                                self.user_data["current_quota"] += transferred_size
                                utils.save_user_data(self.user_data)
                                head_dict = {
                                    "msg_type": "info",
                                    "msg_content": "文件接收完成，文件校验正确。"
                                }
                                self.send_msg_dict(head_dict)
                            else:
                                print("文件md5不匹配")
                                head_dict = {
                                    "msg_type": "error",
                                    "msg_content": "文件接收完成，但文件md5不匹配"
                                }
                                self.send_msg_dict(head_dict)

    def _get_size(self, absolute_file_path):
        path = os.path.normpath("%s/%s" % (self.user_data["home"], absolute_file_path))
        if os.path.exists(path):
            head_dict = {
                "msg_type": "info",
                "transferred_size": os.path.getsize(path)
            }
            self.send_msg_dict(head_dict)
        else:
            head_dict = {
                "msg_type": "error",
                "msg_content": "文件不存在"
            }
            self.send_msg_dict(head_dict)

    def handle_cmd(self):
        while True:
            print("等待接收命令...")
            cmd_dict = self.receive_msg_dict()
            print("cmd_dict:", cmd_dict)
            if cmd_dict["command_type"] == "input":
                full_cmd = cmd_dict["full_command"]
                cmd_list = full_cmd.split()
                print("接收到的命令列表cmd_list:", cmd_list)
                if hasattr(self, "_%s" % (cmd_list[0])):
                    func = getattr(self, "_%s" % (cmd_list[0]))
                    func(cmd_list)
                else:
                    print("没有 %s 这个命令" % cmd_list[0])
                    continue
            elif cmd_dict["command_type"] == "re_transfer":
                print("进行续传任务...")
                cmd_list = [cmd_dict["command_action"], cmd_dict["absolute_file_path"]]
                func = getattr(self, "_%s" % (cmd_dict["command_action"]))
                if cmd_dict["command_action"] == "get_size":
                    func(cmd_dict["absolute_file_path"])
                else:
                    func(cmd_list, cmd_dict["transferred_size"])

    def verify_user_exist(self, username):
        path = "%s/%s.json" % (settings.account_db_dir, username)
        user_path = os.path.normpath(path)
        if os.path.exists(user_path):
            return True
        else:
            return False

    def auth_user(self, user_dict):
        username = user_dict["username"]
        if self.verify_user_exist(username):
            password = user_dict["password"]
            user_data = utils.get_user_data(username)
            pwd = utils.md5(password)
            if pwd == user_data["password"]:
                self.user_data = user_data
                self.user_data["current_dir"] = "/"
                self.user_data["home"] = os.path.normpath(os.path.join(settings.ftp_home_dir, user_data["username"]))
                if not os.path.exists(self.user_data["home"]):
                    os.mkdir(self.user_data["home"])
                return True  # 登录成功
            else:
                return False  # 用户名或密码错误
        else:
            return False  # 用户名不存在

    def receive_msg_dict(self):
        obj = self.conn.recv(4)
        head_size = struct.unpack("i", obj)[0]
        head_bytes = self.conn.recv(head_size)
        msg_dict = json.loads(head_bytes.decode("utf-8"))
        return msg_dict

    def send_msg_dict(self, msg_dict):
        head_bytes = json.dumps(msg_dict).encode("utf-8")
        self.conn.send(struct.pack("i", len(head_bytes)))
        self.conn.send(head_bytes)

    def login(self):
        while True:
            msg_res_dict = self.receive_msg_dict()
            login_res = self.auth_user(msg_res_dict)
            if login_res:
                login_res_msg = {
                    "msg_type": "auth",
                    "msg_content": "successful",
                    "login_res": True
                }
                self.send_msg_dict(login_res_msg)
                break
            else:
                login_res_msg = {
                    "msg_type": "auth",
                    "msg_content": "failed",
                    "login_res": False
                }
                self.send_msg_dict(login_res_msg)

    def run(self):
        while True:
            self.server.bind((settings.host, settings.port))
            self.server.listen(settings.max_queue_size)
            while True:
                try:
                    print("等待客户端连接...")
                    self.conn, self.client_address = self.server.accept()
                    print("客户端已连接，地址：", self.client_address)
                    self.login()
                    self.handle_cmd()
                except Exception as e:
                    print("客户端已断开，地址：", self.client_address)
                    print("异常信息：", e)
                    self.conn.close()
            self.server.close()
