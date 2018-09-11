import socket
import json
import struct
import hashlib
import os
import sys
import platform
import shelve

from client.conf import settings


class FTPClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_dir = "/"

    def receive_command_result(self):
        data_dict = self.receive_msg_dict()
        if data_dict["msg_type"] == "error":
            print(data_dict["msg_content"])
        elif data_dict["msg_type"] == "info_cd":
            print(data_dict["msg_content"])
            if data_dict["current_dir"] == "":
                self.current_dir = "/"
            else:
                self.current_dir = os.path.normpath(data_dict["current_dir"]).replace("\\", "/")
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

    def _exit(self, command_dict):
        exit("Bye Bye!")

    def _help(self, command_dict):
        cmd_help_dict = {
            "get filename": {
                "description": "Download file from server to local",
                "usage": "filename"
            },
            "put filename": {
                "description": "Upload local file to server",
                "usage": "put filename"
            },
            "cd [dirname]": {
                "description": "Change directory",
                "usage": "cd [dirname]"
            },
            "ls [dirname]": {
                "description": "Show directories and files",
                "usage": "ls [dirname]"
            },
            "mkdir [dirname]": {
                "description": "Create directory",
                "usage": "mkdir [dirname]"
            },
            "rmdir [dirname]": {
                "description": "Delete empty directory",
                "usage": "rmdir [dirname]"
            },
            "rm filename": {
                "description": "Delete file",
                "usage": "rm filename"
            },
            "help": {
                "description": "Get help information",
                "usage": "help"
            },
            "exit": {
                "description": "Exit system",
                "usage": "exit"
            },
        }
        print("支持命令".center(50, "-"))
        for cmd in cmd_help_dict:
            print("%-15s %-30s" % (cmd, cmd_help_dict[cmd]["description"]))

    def _ls(self, command_dict):
        self.receive_command_result()

    def _cd(self, command_dict):
        self.receive_command_result()

    def _rm(self, command_dict):
        self.receive_command_result()

    def _rmdir(self, command_dict):
        self.receive_command_result()

    def _mkdir(self, command_dict):
        self.receive_command_result()

    def check_transfer(self):
        while True:
            shelve_obj = shelve.open("db")
            if len(shelve_obj.keys()) == 0:
                break
            transfer_list = []
            print("未传输完成的文件".center(50, "-"))
            for index, file_key in enumerate(shelve_obj):
                if shelve_obj[file_key]["action_type"] == "get":
                    unfinished_file_path = os.path.normpath("%s/%s" % (settings.download_dir, shelve_obj[file_key]["file_name"]))
                    transferred_size = os.path.getsize(unfinished_file_path)
                    transfer_list.append([file_key, transferred_size, shelve_obj[file_key]["file_size"], shelve_obj[file_key]["action_type"]])
                if shelve_obj[file_key]["action_type"] == "put":
                    sent_size_dict = {
                        "command_type": "re_transfer",
                        "command_action": "get_size",
                        "absolute_file_path": file_key
                    }
                    self.send_msg_dict(sent_size_dict)
                    data = self.receive_msg_dict()
                    if data["msg_type"] == "error":
                        print(data["msg_content"])
                    else:
                        transfer_list.append([file_key,  data["transferred_size"], shelve_obj[file_key]["file_size"], shelve_obj[file_key]["action_type"]])  # 传输类型

            for idx, file in enumerate(transfer_list):
                print("序号：%s   文件服务端路径：%s  已传输大小：%s  总共大小：%s    已传输进度：%s    类型：%s"
                      % (idx,
                         transfer_list[idx][0],
                         transfer_list[idx][1],
                         transfer_list[idx][2],
                         "%s%s" % (int((transfer_list[idx][1] / transfer_list[idx][2]) * 100), "%"),
                         transfer_list[idx][3]))

            choice = input("请选择序号继续传输任务(skip 跳过)：").strip()
            if choice == "skip":
                break
            if choice.isdigit():
                choice = int(choice)
                if 0 <= choice <= len(transfer_list):
                    selected_file = transfer_list[choice][0]
                    transfer_size = transfer_list[choice][1]
                    head_dict = {
                        "command_type": "re_transfer",
                        "command_action": transfer_list[choice][3],
                        "absolute_file_path": selected_file,
                        "transferred_size": transfer_size,
                        "full_command": "put %s" % (os.path.basename(selected_file))
                    }
                    self.send_msg_dict(head_dict)
                    func = getattr(self, "_%s" % (transfer_list[choice][3]))
                    func(head_dict)
                else:
                    print("无此选项")
            else:
                print("无此选项")
            shelve_obj.close()

    def _get(self, command_dict):
        data_dict = self.receive_msg_dict()
        if data_dict["msg_type"] == "error":
            print(data_dict["msg_content"])
        else:
            file_name = data_dict["file_name"]
            file_size = data_dict["file_size"]
            file_md5 = data_dict["file_md5"]
            absolute_file_path = os.path.normpath(data_dict["absolute_file_path"]).replace("\\", "/").replace("//", "/")
            local_path = os.path.normpath("%s/%s" % (settings.download_dir, file_name))
            shelve_obj = shelve.open("db")
            if data_dict["transfer_flag"] == "continuingly":
                file_mode = "ab"
            else:
                file_mode = "wb"
                shelve_obj[absolute_file_path] = {"action_type": "get", "file_size": file_size, "file_name": file_name}
            with open(local_path, file_mode) as f:
                receive_size = data_dict["received_size"]
                while receive_size < file_size:
                    data = self.client.recv(settings.receive_bytes)
                    if not data:
                        raise Exception("服务端已断开连接！！")
                    f.write(data)
                    receive_size += len(data)
                    self.show_progress(receive_size, file_size)
                else:
                    print("文件接收完成")
                    if file_md5 == self.md5(file_name):
                        print("文件校验正确")
                        del shelve_obj[absolute_file_path]
                        shelve_obj.close()
                    else:
                        print("文件md5不匹配")

    def _put(self, command_dict):
        cmd_list = command_dict["full_command"].split()
        if len(cmd_list) < 2:
            print("缺少参数")
        elif len(cmd_list) > 2:
            print("参数太多了，只支持1个参数。")
        else:
            path = os.path.normpath("%s/%s" % (settings.download_dir, cmd_list[1]))
            if os.path.exists(path):
                if not os.path.isdir(path):
                    file_name = os.path.basename(path)
                    file_size = os.path.getsize(path)
                    head_dict = {
                        "msg_type": "info",
                        "file_name": file_name,
                        "file_size": file_size,
                        "file_md5": self.md5(file_name),
                        "transferred_size": command_dict["transferred_size"]
                    }
                    self.send_msg_dict(head_dict)
                    verify_quota_res = self.receive_msg_dict()
                    if verify_quota_res["msg_type"] == "error":
                        print(verify_quota_res["msg_content"])
                    else:
                        shelve_obj = shelve.open("db")
                        sent_size = command_dict["transferred_size"]
                        absolute_file_path = os.path.normpath("%s/%s" % (self.current_dir, file_name)).replace("\\", "/").replace("//", "/")
                        if sent_size == 0:
                            shelve_obj[absolute_file_path] = {"action_type": "put",
                                                              "transferred_size": sent_size,
                                                              "file_size": file_size,
                                                              "file_name": file_name}
                        with open(path, "rb") as f:
                            if sent_size != 0:
                                f.seek(sent_size)
                            for line in f:
                                self.client.send(line)
                                sent_size += len(line)
                                self.show_progress(sent_size, file_size)
                            else:
                                msg_data = self.receive_msg_dict()
                                print(msg_data["msg_content"])
                                if command_dict["command_type"] == "input":
                                    del shelve_obj[absolute_file_path]
                                else:
                                    del shelve_obj[command_dict["absolute_file_path"]]
                                shelve_obj.close()
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
        if not obj:
            return False
        else:
            head_size = struct.unpack("i", obj)[0]
            head_bytes = self.client.recv(head_size)
            msg_dict = json.loads(head_bytes.decode("utf-8"))
            return msg_dict

    def command_interactive(self):
        while True:
            cmd_input = input("[%s]>>>: " % (self.current_dir)).strip()
            if not cmd_input:
                continue

            cmd_list = cmd_input.split()
            if hasattr(self, "_%s" % (cmd_list[0])):
                command_dict = {
                    "command_type": "input",
                    "command_action": cmd_list[0],
                    "full_command": cmd_input,
                    "transferred_size": 0
                }
                self.send_msg_dict(command_dict)
                func = getattr(self, "_%s" % (cmd_list[0]))
                func(command_dict)
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
                    self.check_transfer()
                    self.command_interactive()
        except ConnectionResetError:
            self.client.close()
