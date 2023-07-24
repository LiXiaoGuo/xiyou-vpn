# xiyou-vpn

西游VPN专用，使用opennection连接西游服务器，然后通过tinyproxy做流量转发，局域网的其他设备就可以通过tinyproxy突破西游客户端限制。

提供pac文件，每天凌晨一点重新生成，使用地址：`ip:port/proxy.pac`

### 功能
- [x] 断线重连
- [x] 重连时尽量不会挤掉其他设备
- [x] 局域网设备http代理访问
- [x] 提供pac文件

### 配置文件
```shell
mkdir -p /data/docker/xiyou-vpn
vim /data/docker/xiyou-vpn/vpn.conf
```
vpn.conf内容
```json5
{
    "domain":"西游连接地址",
    "username":"西游VPN账号",
    "password":"西游VPN密码",
    "pac_proxy":"PROXY 192.168.165.153:11021;DIRECT;"
}
```
`pac_proxy`是pac文件中的代理地址，需要根据实际情况修改

### docker使用

```shell
# 拉取镜像
docker pull extendslg/xiyou-vpn

# 启动
docker run -itd --restart=always  -p 11020:8000 -p 11021:8888 -v /data/docker/xiyou-vpn:/app/data --privileged=true xiyou-vpn
```
- 配置了`--restart=always`后出了问题就会自动重启
- 8000端口是pac文件用的下载端口，8888端口是tinyproxy端口转发用的
- `--privileged=true`必须要，要不然服务无法正常启动