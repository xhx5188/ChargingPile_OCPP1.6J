# 					充电桩OCPP接口自动化测试框架

- ### 介绍

  该测试框架目前只适用于充电桩的ocpp接口测试。主要由以下部分组成：pytest测试框架，ocpp server，allure测试报告生成，WIFI控制继电器模块，蓝牙通信模块。

  开发语言选择Python，经过封装，通过简单地调用固定接口，即可实现测试用例的脚本化。例如，以下是一个octt中验证解锁枪失败的测试用例，实现过程为：

  ![image](https://github.com/pj635/ocpp_test/raw/master/screenshots/sample1.png)

- ### 优缺点

  缺点：虽然已将框架进行高度封装，但还是要求测试人员有一定的Python语言基础才能熟练掌握。而且是脚本化的工具，不如octt有界面的操作方式，对小白不太友好。

  优点：支持测试用例的自动执行，避免每个版本都有进行一遍手动测试；测试用例可根据实际场景进行自定义，便于发掘隐藏bug和复现复杂场景中的bug；支持自动生成测试报告，自动插拔枪，自动上线电。

- ### 安装使用

  1. 分别安装Python3.7，java1.8，allure2.16及以上。

  2. 本地安装git和git bash工具，下载框架源码：git clone https://github.com/pj635/ocpp_test

  3. 关闭本地防火墙，连接guest wifi 网络，查询本地IP

  4. 充电桩也连接guest wifi网络，设置ocpp服务器地址为上一步查询到的IP，uri为"/"

  5. 进入ocpp_test目录，添加requirements.txt文件中的库

  6. 将wifi控制继电器的接线按如下图接好，枪的模拟电阻接继电器常开，电源控制接继电器常闭。

     ![image](https://github.com/pj635/ocpp_test/raw/master/screenshots/sample2.jpg)

  7. 参考ocpp_test/detail.md文件，更改websocket库和ocpp库的源码

  8. 按照实际情况修改ocpp_test/config.yaml配置文件中的配置信息，分别是wifi控制继电器的IP，蓝牙串口模块的端口号+蓝牙mac地址，充电桩SN。
  
  9. 交流桩的测试用例，可通过ocpp_test/testcase/start.sh执行。

