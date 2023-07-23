# xiyou-vpn

西游VPN专用，使用opennection连接西游服务器，然后通过tinyproxy做流量转发，局域网的其他设备就可以通过tinyproxy突破西游客户端限制。

提供pac文件，每天凌晨一点重新生成，使用地址：`ip:port/proxy.pac`

### 功能
- [x] 断线重连
- [x] 重连时尽量不会挤掉其他设备
- [x] 局域网设备http代理访问
- [x] 提供pac文件