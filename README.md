修改标准库：
  1.更改websocket库：由于我们充电桩不支持回复websocketPing功能，所以需要去掉OCPP服务器主动发送websocketPing的功能
  ![image](https://github.com/pj635/ocpp_test/raw/master/screenshots/update_websocket1.png)