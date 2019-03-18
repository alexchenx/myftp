# MyFTP服务使用指南
本服务可支持在Windows和Linux平台运行，支持多用户并发运行，默认最大支持10个用户同时运行，启动前请进行必要的IP和端口配置。  
服务端数据默认保存在：myftp/server/FTP_DATA  
客户端数据默认保存在：myftp/client/{username}  

## 配置说明
服务端配置文件：myftp/server/conf/settings.py  
客户端配置文件：myftp/client/conf/settings.py  

## 测试用户
测试用户1：alex  密码：123456  
测试用户2：jack  密码：123456

## 用户配置：
用户配置目录：myftp/server/db/   
配置用户后，如果用户home目录不存在，登录成功后系统将会自动创建。  
   
配置格式如下：  
文件名：alex.json  
文件内容（quota默认1G的字节数，即1073741824）：  
{
  "username": "alex",
  "password": "e10adc3949ba59abbe56e057f20f883e",
  "home": "alex",
  "quota": 1073741824,
  "current_quota": 0,
  "current_dir": ""
}

## 启动程序
服务端：python3 myftp/server/bin/server_run.py  
客户端：python3 myftp/client/bin/client_run.py

## 本系统支持命令
#### get
说明：从服务器下载指定文件   
用法：get filename

#### put
说明：从客户端上传指定文件至服务器，不支持指定路径   
用法：put filename

#### ls
说明： 查看当前目录下的目录及文件   
用法：ls [dirname]

#### cd
说明：切换目录   
用法：cd [dirname]

#### mkdir
说明：创建目录   
用法：mkdir [dirname]

#### rmdir
说明：删除空目录   
用法：rmdir [dirname]

#### rm
说明：删除指定的文件   
用法：rm [filename]

#### exit
说明：退出系统  
用法：exit






