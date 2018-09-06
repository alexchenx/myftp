import socket
import json
import struct
import hashlib
import os
import sys
import platform

from client.conf import settings


class FTPClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_command_result(self, cmds):
        data_dict = self.receive_msg_dict()
        if data_dict["msg_type"] == "error":
            print(data_dict["msg_content"])
        elif data_dict["msg_type"] == "info_cd":
            print(data_dict["msg_content"])
        else:
            content_size = data_dict["msg_size"]
            receive_size = 0
            receive_data = b""
            while receive_size < content_size:
                data = self.client.recv(settings.receive_bytes)
                receive_data += data
                receive_size += len(data)
            if platform.uname()[0] == "Windows":
                print(receive_data.decode("GBK"))
            else:
                print(receive_data.decode("UTF-8"))

    def _exit(self, cmds):
        exit("Bye Bye!")

    def _help(self, cmds):
        cmd_help_dict = {

            "get": {
                "description": "Download file from server to local",
                "usage": ""
            },
            "put": {
                "description": "Upload local file to server",
                "usage": ""
            },
            "cd": {
                "description": "Change directory",
                "usage": ""
            },
            "ls": {
                "description": "Show directories and files",
                "usage": ""
            },
            "mkdir": {
                "description": "Create directory",
                "usage": ""
            },
            "rmdir": {
                "description": "Delete empty directory",
                "usage": ""
            },
            "rm": {
                "description": "Delete file",
                "usage": ""
            },
            "help": {
                "description": "Get help information",
                "usage": ""
            },
            "exit": {
                "description": "Exit system",
                "usage": ""
            },
        }
        print("支持命令".center(50, "-"))
        for cmd in cmd_help_dict:
            print("%-5s    %-20s" % (cmd, cmd_help_dict[cmd]["description"]))

    def _ls(self, cmds):
        self.receive_command_result(cmds)

    def _cd(self, cmds):
        self.receive_command_result(cmds)

    def _rm(self, cmds):
        self.receive_command_result(cmds)

    def _rmdir(self, cmds):
        self.receive_command_result(cmds)

    def _mkdir(self, cmds):
        self.receive_command_result(cmds)

    def _get(self, cmds):
        data_dict = self.receive_msg_dict()
        if data_dict["msg_type"] == "error":
            print(data_dict["msg_content"])
        else:
            file_name = data_dict["file_name"]
            file_size = data_dict["file_size"]
            file_md5 = data_dict["file_md5"]
            with open("%s/%s" % (settings.download_dir, file_name), "wb") as f:
                receive_size = 0
                while receive_size < file_size:
                    data = self.client.recv(settings.receive_bytes)
                    f.write(data)
                    receive_size += len(data)
                    self.show_progress(receive_size, file_size)
                else:
                    print("文件接收完成")
                    if file_md5 == self.md5(file_name):
                        print("文件校验正确")
                    else:
                        print("文件md5不匹配")


    def _put(self, cmds):
        if len(cmds) < 2:
            print("缺少参数")
        elif len(cmds) > 2:
            print("参数太多了，只支持1个参数。")
        else:
            path = os.path.join(settings.download_dir, cmds[1])
            if os.path.exists(path):
                if not os.path.isdir(path):
                    file_name = os.path.basename(path)
                    file_size = os.path.getsize(path)
                    head_dict = {
                        "msg_type": "info",
                        "file_name": file_name,
                        "file_size": file_size,
                        "file_md5": self.md5(file_name)
                    }
                    self.send_msg_dict(head_dict)
                    verify_quota_res = self.receive_msg_dict()
                    if verify_quota_res["msg_type"] == "error":
                        print(verify_quota_res["msg_content"])
                    else:
                        sent_size = 0
                        with open(path, "rb") as f:
                            for line in f:
                                self.client.send(line)
                                sent_size += len(line)
                                self.show_progress(sent_size, file_size)
                            else:
                                msg_data = self.receive_msg_dict()
                                print(msg_data["msg_content"])
                else:
                    print("目录不能上传")
                    head_dict = {
                        "msg_type": "error",
                        "msg_content": "目录不能上传"
                    }
                    self.send_msg_dict(head_dict)
            else:
                print("文件不存在")
                head_dict = {
                    "msg_type": "error",
                    "msg_content": "文件不存在"
                }
                self.send_msg_dict(head_dict)

    def md5(self, content):
        ha = hashlib.md5()
        ha.update(bytes(content, encoding="utf-8"))
        md5_value = ha.hexdigest()
        return md5_value

    def show_progress(self, receive_size, file_size):
        s = "\r进度：%s %d%% " % ("#" * int((receive_size / file_size) * 50), (receive_size / file_size) * 100)
        sys.stdout.write(s)
        sys.stdout.flush()

    def send_msg_dict(self, msg_dict):
        head_bytes = json.dumps(msg_dict).encode("utf-8")
        self.client.send(struct.pack("i", len(head_bytes)))
        self.client.send(head_bytes)

    def receive_msg_dict(self):
        obj = self.client.recv(4)
        head_size = struct.unpack("i", obj)[0]
        head_bytes = self.client.recv(head_size)
        msg_dict = json.loads(head_bytes.decode("utf-8"))
        return msg_dict

    def command_interactive(self):
        while True:
            cmd_input = input("command>>>: ").strip()
            if not cmd_input: continue

            cmd_list = cmd_input.split()
            if hasattr(self, "_%s" % (cmd_list[0])):
                self.client.send(cmd_input.encode("utf-8"))
                func = getattr(self, "_%s" % (cmd_list[0]))
                func(cmd_list)
            else:
                print("没有 %s 这个命令" % cmd_list[0])

    def login(self):
        while True:
            username = input("username: ").strip()
            password = input("password: ").strip()
            if not username or not password:
                print("用户名或密码不能为空")
                continue
            user_dict = {"username": username, "password": password}
            self.send_msg_dict(user_dict)
            login_res_dict = self.receive_msg_dict()
            if login_res_dict["login_res"]:
                print("登录成功")
                return True
            else:
                print("用户名或密码错误")
                return False

    def run(self):
        print("欢迎使用MyFTP服务^_^")
        try:
            self.client.connect((settings.host, settings.port))
            while True:
                if self.login():
                    self.command_interactive()
        except ConnectionResetError:
            self.client.close()
