#!/bin/bash

# 注释掉ip白名单，启动 tinyproxy
sed -i '/^Allow/ s/^/#/' /etc/tinyproxy/tinyproxy.conf
service tinyproxy restart


# 启动pac文件生成
nohup python3 /app/update_pac.py > /dev/null 2>&1 &

# 启动 文件服务
cd /app/file
nohup python3 -m http.server > /dev/null 2>&1 &

#启动西游
cd /app
python3 /app/start_vpn.py