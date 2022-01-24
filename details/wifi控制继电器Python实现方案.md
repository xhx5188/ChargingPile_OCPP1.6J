# WiFi控制继电器python方案实现

- ### 需求场景

  针对本公司充电桩产品中，为实现自动化测试，需要模拟充电桩一些手工操作，比如插拔枪，上下电，甚至故障的模拟。

- ### 总体思路

  通过脚本控制WiFi继电器模块，对一些手工的开关量操作进行模拟。

![image](https://github.com/pj635/ocpp_test/raw/master/screenshots/wifi1.png)

​		Python客户端脚本发送一些固定指令给esp8266WiFi模组，模组根据具体的指令控制继电器的开合。如下为		一个脚本通过wifi模块控制插枪/拔枪的例子：

​	

```
import socket
from time import sleep
import yaml

class Connector():
    @classmethod
    # 插枪方法
    def slot(cls, path="../../config.yaml"):
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f)
            # 从config.yaml文件中读取wifi模组的ip和port
            ip = cfg['connector']['STAIP']
            port = cfg['connector']['port']

        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        data = bytes.fromhex("a00101a2") # 打开第一路继电器
        s.send(data)
        s.close()

    @classmethod
    # 拔枪方法
    def unslot(cls, path="../../config.yaml"):
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f)
            ip = cfg['connector']['STAIP']
            port = cfg['connector']['port']

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        data = bytes.fromhex("a00100a1") # 关闭第一路继电器
        s.send(data)
        s.close()

```

config.yaml文件配置

```
connector:
  STAIP: "10.10.41.44"   #每个WiFi模组都不一样，根据AT+CIFSR查询。
  port: 8080

```

- ### 配置WIFI模组的server模式

配置esp8266WIFI模组：将模组连接串口调试工具，波特率设置115200，**串口工具配置自动换行**；按S1开关按	钮使**蓝灯点亮**。依次发送：
	AT+CWMODE=3                  #配置WiFi模组为server模式
	AT+CWJAP=“wifi名称”,”wifi密码”    #连接公司Guest wifi网络
	AT+CIFSR                       #查询模组的IP地址，以便与python脚本交互。

