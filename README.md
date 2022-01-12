修改标准库：
  1.更改websocket库：由于我们充电桩不支持回复websocketPing功能，所以需要去掉OCPP服务器主动发送websocketPing的功能。
  ![image](https://github.com/pj635/ocpp_test/raw/master/screenshots/update_websocket1.png)
  
  
  ![image](https://github.com/pj635/ocpp_test/raw/master/screenshots/update_websocket2.png)
  
  2.更改OCPP库：由于我们的小特tcu产品的ocpp协议做了部分修改，需要做出相应的适配。
	远程启动充电增加部分字段,故远程启动充电请求中需要增加以下字段：
	![image](https://github.com/pj635/ocpp_test/raw/master/screenshots/update_ocpp1.png)

	
	去掉ocpp json格式校验代码：
	![image](https://github.com/pj635/ocpp_test/raw/master/screenshots/update_ocpp2.png)

  