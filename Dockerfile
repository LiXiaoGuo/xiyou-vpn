# 使用适当的基础镜像，这里使用Ubuntu作为例子
FROM ubuntu:22.04

## 更换apt镜像
ADD sources.list /etc/apt/

WORKDIR /app

# 安装所需软件和依赖
RUN mkdir /app/data && mkdir /app/file && apt-get update && \
apt-get install -y openconnect python3 python3-pip tinyproxy cron && \
pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple && \
echo "0 1 * * *  /usr/bin/python3 /app/update_pac.py" >> /etc/crontab

# 设置Tinyproxy配置（如果需要自定义配置）
# COPY tinyproxy.conf /etc/tinyproxy/tinyproxy.conf

# 暴露Tinyproxy端口，如果有必要
EXPOSE 8888
EXPOSE 8000

# 设置工作目录，可选
#WORKDIR /app

#RUN mkdir /app/data

# 将其他文件复制到容器中（如果有需要）
COPY start.sh /app
COPY start_vpn.py /app
COPY update_pac.py /app
COPY pac-template /app
COPY delegated-apnic-latest /app

RUN chmod a+x /app/start.sh

# 设置环境变量（如果需要）
# ENV YOUR_ENV_VARIABLE value

# 容器启动时执行的命令，可以使用shell格式或者CMD格式
  #CMD python3 /app/start_vpn.py
# 或者
# CMD your_command


# 或者可以使用ENTRYPOINT指定执行的命令，可以与CMD组合使用
# ENTRYPOINT ["/path/to/your/executable"]
ENTRYPOINT ["/app/start.sh"]