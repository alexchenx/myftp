# MyFTP服务使用指南
本服务可支持在Windows和Linux平台运行，启动前请根据不同平台配置相应的服务端ftp_home_dir路径和客户端download_dir路径，正确配置后，系统将会自动创建。

## 测试用户
测试用户1：alex 密码：123456  
测试用户2：jack 密码：123456

## 配置说明
服务端配置文件：myftp/server/conf/settings.py  
客户端配置文件：myftp/client/conf/settings.py  
【特别说明】：在Windows环境下服务端请将ftp_home_dir配置到C盘，否则可能会出现异常。

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
服务端：myftp/server/bin/server_run.py  
客户端：myftp/client/bin/client_run.py

## 本系统支持命令

### 通用命令
#### get
说明：从服务器下载指定文件   
用法：get filename

#### put
说明：从客户端上传指定文件至服务器，不支持指定路径   
用法：put filename

#### cd
说明：切换目录   
用法：cd [dirname]

#### rmdir
说明：删除空目录   
用法：rmdir [dirname]

### Windows平台下：
#### dir
说明： 查看当前目录下的目录及文件   
用法：dir [dirname]

#### del
说明：删除指定文件  
用法：del filename

### Linux平台:
#### ls
说明： 查看当前目录下的目录及文件   
用法：ls [dirname]

#### rm
说明：删除指定的文件   
用法：rm [filename]



              
            

       

# 需求
作业题目: 开发一个支持多用户在线的FTP程序

要求：

1.用户加密认证   
2.允许同时多用户登录   
3.每个用户有自己的家目录 ，且只能访问自己的家目录   
4.对用户进行磁盘配额，每个用户的可用空间不同   
5.允许用户在ftp server上随意切换目录    
6.允许用户查看当前目录下文件    
7.允许上传和下载文件，保证文件一致性(md5)   
8.文件传输过程中显示进度条    
9.附加功能：支持文件的断点续传



