import json
import os
import re
import subprocess
import time
import traceback

import requests


def get_config():
    """读取vpn配置"""
    return json.load(open("/app/data/vpn.conf"))


def get_login_info(conf):
    """获取登陆信息，并数值化最后在线时间"""
    pattern = re.compile(r'(?<=calibration=)\d+\.?\d*')
    datas = requests.post("https://crteam.cn:1443/api/v3/login/", json=conf,
                          headers={"Host": "crteam.cn:1443", "ver": "2.9.5.0"}).json()["sessions_to_expire"]
    for data in datas:
        try:
            time_str = data["last_online_time_ago"]
            t = pattern.findall(time_str)[0]
            if "".find("分") > 0:
                u = 60
            elif time_str.find("时") > 0:
                u = 3600
            elif time_str.find("天") > 0:
                u = 86400
            elif time_str.find("周") > 0:
                u = 604800
            elif time_str.find("月") > 0:
                u = 2592000
            elif time_str.find("年") > 0:
                u = 31536000
            else:
                u = 1
            data["last_online_time_ago"] = t * u
        except:
            data["last_online_time_ago"] = 0
    return datas


def get_current_title():
    """获取当前的title"""
    try:
        with open("/app/data/vpn_current_title", 'r+') as f:
            return f.readline().strip()
    except:
        return ""


def save_current_title(new_login, old_login):
    """对比新旧title，保存当前的title"""
    tmps = []
    for nl in new_login:
        tmp = True
        for ol in old_login:
            if nl["title"] == ol["title"]:
                tmp = False
        if tmp:
            tmps.append(nl)
    current_title = min(tmps, key=lambda x: x['last_online_time_ago'])["title"]
    print("\n已经保存当前的Title：", current_title)
    with open("/app/data/vpn_current_title", 'w+') as f:
        f.write(current_title)


def start_vpn(conf):
    """启动西游的核心逻辑"""
    tmp_current_title = get_current_title()
    current_title = ""
    old_login = get_login_info(conf)
    if tmp_current_title != "":
        for ol in old_login:
            if ol["title"] == tmp_current_title:
                current_title = tmp_current_title
    if current_title == "":
        current_title = max(old_login, key=lambda x: x['last_online_time_ago'])["title"]

    import pty
    # 使用pty.spawn创建一个伪终端并执行命令
    command = ['/bin/bash']  # 或者其他你想要模拟的Shell命令
    master, slave = pty.openpty()

    def write(cmd):
        os.write(master, f"{cmd}\n".encode())

    def wait_echo(keywords):
        total_output = ""
        key = ""
        while key == "":
            # 字节数尽可能大一点，避免字符串重中间截断了，导致下面的字符串匹配出问题
            output = os.read(master, 8192).decode('utf-8', 'ignore')
            total_output += output
            print(output, end='')
            # print("====================")
            if isinstance(keywords, (list, tuple)):
                # print(output.find(keywords[0]))
                result = next(filter(lambda x: re.search(x, total_output) is not None, keywords), None)
                if result is not None:
                    key = result
                    # print("key=",key)
                    break
            else:
                # print(keywords,type(keywords))
                if re.search(keywords, total_output):
                    key = keywords
                    # print("key=",key)
                    break

        return key, total_output

    p = subprocess.Popen(command, stdin=slave, stdout=slave, stderr=slave, text=True, bufsize=1)
    # 输入连接命令
    write(f"openconnect {conf['domain']}")
    print("\n-- 正在连接服务器")
    # 输入账号
    wait_echo("Username:")
    write(conf["username"])
    print("\n-- 正在输入账号")
    # 输入密码
    wait_echo("Password:")
    write(conf["password"])
    print("\n-- 正在输入密码")

    # 判断是成功了还是要输入用户组
    key, op = wait_echo([r"Group: \[([^\]]+)]:", "Connected as"])
    if key != "Connected as":
        goup = get_select_group(op, current_title)
        write(goup)
        print("-- 正在输入用户组:", goup)

        # 等待连接成功
        wait_echo("SSL connected")
        print("\n—— VPN已连接")

    time.sleep(5)
    # 保存当前的title
    new_login = get_login_info(conf)
    save_current_title(new_login, old_login)
    try:
        # 等待程序退出
        wait_echo(["exiting", "server disconnect"])
        print("\n-- VPN连接已断开")

        os.close(master)
        os.close(slave)
        p.terminate()
        print("\n-- 清理资源")
    except:
        print("\n-- 清理资源失败")
        traceback.print_exc()
        pass
    print("\n-- 5s后重新连接VPN")
    time.sleep(5)
    return start_vpn(conf)
    # p.communicate()
    # # 阻塞进程
    # while True:
    #     time.sleep(30)


def get_select_group(output, last_title):
    """获取匹配到的用户组"""
    if last_title == "":
        last_title = "[^[]"
    else:
        last_title = last_title.replace("|", r"\|")
    pattern = rf'([^|[]+): {last_title}'
    # 使用正则表达式进行匹配
    result = re.search(pattern, output)
    # 使用正则表达式进行匹配
    # 提取匹配到的内容
    if result:
        matched_content = result.group(1)
        print("\n匹配到的内容:", matched_content)
        return matched_content
    else:
        print("\n未匹配到内容")
        return "1"


if __name__ == "__main__":
    try:
        conf = get_config()
    except:
        print("没有找到配置文件")
        traceback.print_exc()
    if conf:
        # 启动vpn
        start_vpn(conf)
        # 启动端口转发
